package ibis.amuse;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.util.ArrayList;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Class representing a code that is used via a loopback socket interface.
 * 
 * @author Niels Drost
 * 
 */
public class SocketCodeInterface extends CodeInterface {

    private static final Logger logger = LoggerFactory
            .getLogger(SocketCodeInterface.class);

    private static final int ACCEPT_TRIES = 20;
    private static final int ACCEPT_TIMEOUT = 1000; // ms

    private static final String[] ENVIRONMENT_BLACKLIST = { "JOB_ID", "PE_",
            "PRUN_", "JOB_NAME", "JOB_SCRIPT", "OMPI_" };

    private final File executable;

    // local socket communication stuff

    private final ServerSocketChannel serverSocket;

    private final SocketChannel socket;

    private final Process process;

    private AmuseMessage requestMessage;
    private AmuseMessage resultMessage;

    private final OutputPrefixForwarder out;
    private final OutputPrefixForwarder err;

    SocketCodeInterface(String workerID, PoolInfo poolInfo, String codeName,
            String codeDir, String amuseHome, String mpirun, int nrOfWorkers,
            int mpiCollectorPort) throws Exception {
        super(workerID, poolInfo);

        AmuseMessage initRequest = receiveInitRequest();

        try {

            executable = new File(amuseHome + File.separator + codeDir
                    + File.separator + codeName);
            if (!executable.isFile()) {
                throw new IOException("Cannot find executable for code "
                        + codeName + ": " + executable);
            }
            
            if (!executable.canExecute()) {
                throw new IOException(executable + " is not executable");
            }

            serverSocket = ServerSocketChannel.open();
            serverSocket.socket().bind(null);

            File hostFile = File.createTempFile("host", "file");

            FileWriter writer = new FileWriter(hostFile);
            for (String hostname : poolInfo.getWorkerHostList(nrOfWorkers)) {
                writer.write(hostname + "\n");
            }
            writer.flush();
            writer.close();

            logger.info("host file = " + hostFile.getAbsolutePath());

            ProcessBuilder builder = new ProcessBuilder();

            for (String key : builder.environment().keySet()
                    .toArray(new String[0])) {
                for (String blacklistedKey : ENVIRONMENT_BLACKLIST) {
                    if (key.startsWith(blacklistedKey)) {
                        builder.environment().remove(key);
                        logger.info("removed " + key + " from environment");
                    }
                }
            }

            if (mpirun == null) {
                mpirun = "mpirun";
            }

            builder.command(mpirun, "-machinefile", hostFile.getAbsolutePath(),
                    executable.toString(),
                    Integer.toString(serverSocket.socket().getLocalPort()),
                    "--ibis-monitor-port", Integer.toString(mpiCollectorPort));

            // make sure there is an "output" directory for a code to put output
            // in
            new File("output").mkdir();

            process = builder.start();

            out = new OutputPrefixForwarder(process.getInputStream(),
                    System.out, "stdout of " + codeName + ": ");
            err = new OutputPrefixForwarder(process.getErrorStream(),
                    System.err, "stderr of " + codeName + ": ");

            logger.info("process started");

            socket = acceptConnection(serverSocket);

            logger.info("connection established");

        } catch (Throwable e) {
            sendInitReply(initRequest.getCallID(), e);

            end();

            throw new Exception("error on starting socket code", e);
        }
        sendInitReply(initRequest.getCallID());
    }

    private static SocketChannel acceptConnection(
            ServerSocketChannel serverSocket) throws IOException {
        serverSocket.configureBlocking(false);
        for (int i = 0; i < ACCEPT_TRIES; i++) {
            SocketChannel result = serverSocket.accept();

            if (result != null) {
                return result;
            }
            try {
                Thread.sleep(ACCEPT_TIMEOUT);
            } catch (InterruptedException e) {
                // IGNORE
            }
        }
        throw new IOException(
                "worker not started, socket connection failed to initialize");
    }

    @Override
    void call() throws IOException {
        logger.debug("performing call with function ID "
                + requestMessage.getFunctionID());
        requestMessage.writeTo(socket);
        resultMessage.readFrom(socket);
        logger.debug("done performing call with function ID "
                + requestMessage.getFunctionID() + " error = "
                + resultMessage.getError());
    }

    @Override
    void end() {
        if (process != null) {
            process.destroy();
        }

        if (out != null) {
            // wait for out and err a bit
            try {
                out.join(1000);
            } catch (InterruptedException e) {
                // IGNORE
            }
        }

        if (err != null) {
            try {
                err.join(1000);
            } catch (InterruptedException e) {
                // IGNORE
            }
        }

        super.end();
    }

    @Override
    void setRequestMessage(AmuseMessage message) {
        this.requestMessage = message;
    }

    @Override
    void setResultMessage(AmuseMessage message) {
        this.resultMessage = message;
    }

}
