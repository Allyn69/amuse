
class BinaryTreesOnAParticleSet(object):

    def __init__(self, particles_set, name_of_firstchild_attribute, name_of_secondchild_attribute):
        self.particles_set = particles_set
        self.name_of_firstchild_attribute = name_of_firstchild_attribute
        self.name_of_secondchild_attribute = name_of_secondchild_attribute
        
        
    def iter_roots(self):
        binaries = self._binaries()
        binaries_children1 = self._get_inner_nodes(binaries, self.name_of_firstchild_attribute)
        binaries_children2 = self._get_inner_nodes(binaries, self.name_of_secondchild_attribute)
    
        roots = (binaries - (binaries_children1 + binaries_children2))
        
        for particle in roots:
            yield BinaryTreeOnParticle(particle, self.name_of_firstchild_attribute, self.name_of_secondchild_attribute)
            

    def _binaries(self):
        return self.particles_set.select_array(lambda x : x.key > 0, [self.name_of_firstchild_attribute,])


    def _get_inner_nodes(self, set, name_of_attribute):
        children = getattr(set, name_of_attribute)
        return children.select_array(lambda x : x > 0, ["key",]).select_array(lambda x : x.key > 0, [name_of_attribute,])

class BinaryTreeOnParticle(object):

    def __init__(self, particle, name_of_firstchild_attribute = "child1" , name_of_secondchild_attribute = "child2"):
        self.particle = particle
        self.name_of_firstchild_attribute = name_of_firstchild_attribute
        self.name_of_secondchild_attribute = name_of_secondchild_attribute
        
        
    def iter_descendants(self):
        stack = [self.particle]
        while len(stack) > 0:
            current = stack.pop()
            children = []
            child1 = getattr(current, self.name_of_firstchild_attribute)
            if not child1 is None:
                yield child1
                children.append(child1)
                
            child2 = getattr(current, self.name_of_secondchild_attribute)
            if not child2 is None:
                yield child2
                children.append(child2)
            
            stack.extend(reversed(children))
    def iter_leafs(self):
        stack = [self.particle]
        while len(stack) > 0:
            current = stack.pop()
        
            children = []
            child1 = getattr(current, self.name_of_firstchild_attribute)
            if not child1 is None:
                children.append(child1)
            
            child2 = getattr(current, self.name_of_secondchild_attribute)
            if not child2 is None:
                children.append(child2)
            
            stack.extend(reversed(children))
        
            if len(children) == 0:
                yield current





    def iter_inner_nodes(self):
        stack = [self.particle]
        while len(stack) > 0:
            current = stack.pop()
        
            children = []
            child1 = getattr(current, self.name_of_firstchild_attribute)
            if not child1 is None:
                children.append(child1)
            
            child2 = getattr(current, self.name_of_secondchild_attribute)
            if not child2 is None:
                children.append(child2)
            
            stack.extend(reversed(children))
        
            if len(children) > 0:
                yield current

    def get_inner_nodes_subset(self):    
        keys = [x.key for x in self.iter_inner_nodes()]
        return self.particle.particles_set._subset(keys)

    def get_descendants_subset(self):    
        keys = [x.key for x in self.iter_descendants()]
        return self.particle.particles_set._subset(keys)

    def get_leafs_subset(self):    
        keys = [x.key for x in self.iter_leafs()]
        return self.particle.particles_set._subset(keys)



