import web
import json
import ast
import model
import random
import ga

urls = (
        '/', 'Index',
        '/fitness/(.+)', 'Fitness',
        '/save_fitness/(.+)', 'SaveFitness',
        '/terminate', 'Terminate',)

render = web.template.render('templates/', base='layout')
app = web.application(urls, globals())
title = 'GA Server'

class GA:
    """Miniature genetic algorithm library"""

    def create_indi(self,indi_id, trait_id, generation, fitness, note, duration):
        """Spawn an individual. Returns a dictionary containing an individual
        with the desired features"""
        indi = {
            "indi_id": indi_id,
            "trait_id": trait_id,
            "generation": generation,
            "fitness": fitness,
            "note": note,
            "user_note": note,
            "duration": duration,
        }
        return indi

    def fate(self,indi_id):
        """Use the individual that was just evaluated to determine
        where we are in the grand scheme of things. How many more individuals
        of the current generation need to be evaluated? Are the termination
        requirements met? Are we ready to move to the next generation? Etc..."""

        max_gen = model.params_max_gen()['max_gen']        
        current_generation = model.pop_current_generation(indi_id)['generation']
        max_indi = model.pop_max_indi(current_generation)[0]['indi_id']    

        if indi_id == max_indi:
            # termination requirements met?
            if current_generation == max_gen:
                raise web.seeother('/terminate')
            else:
                # current generation over, start mating!
                self.select(current_generation)
        elif indi_id < max_indi:
            raise web.seeother('/fitness/'+str(indi_id+1))
        else:
            raise web.seeother('/terminate')

    def select(self, current_generation):
        """Selection phase -- right now I've only implemented tournament
        selection. Use current_generation to grab all individuals of 
        previous generation"""

        num_rounds = 2
        k = 2
        winner = []

        for i in range(num_rounds):
            winner.append(self.tournament(k,current_generation))
      
        child = self.crossover(random.choice(winner), random.choice(winner))

    def tournament(self, k, current_generation):
        """Tournament Selection

        k = subset size
    
        1. a random subset of size, k, from the given generation is extracted 
        2. sort the pool by fitness value
        3. return the winner, the individual with the highest fitness value"""

        # find k best individuals in population
        population = model.pop_population_by_generation(current_generation)
        pool = []
        for i in range(k):
            individual = random.choice(population)
            if individual not in pool:
                pool.append(individual)

        # select individual with the highest fitness score
        winner = sorted(pool, key=lambda x: -x['fitness'])[0]
        return winner
    
    def crossover(self, parent1, parent2):
        """Do tomorrow..."""
        pass

class Index:
    def GET(self):
        """Render the parameter initialization view"""
        model.pop_clear_conn()
        model.params_clear_conn()

        model.params_save({"max_gen":1})
        pop_size = 5
        num_traits = 10
        notes = ['A','B','C','D','E','F','G']
        for ps in range(pop_size):
            for nt in range(num_traits):
                chromosome = GA().create_indi(ps, nt, 0, 0, random.choice(notes), 1)
                model.pop_save_individual(chromosome)
                #print chromosome
        raise web.seeother('/fitness/0')

    def POST(self):
        pass

class Fitness:
    """This is an interactive fitness function, i.e. the individual is scored
    by the user. The user is shown a melody and is allowed to make X modifications 
    to it (e.g. re-order up to X traits). The euclidean dsitance is taken for the original melody
    and the user-modified melody. Ideally, we want a fitness score of 0 because that
    means the user liked what the computer presented."""
    
    def GET(self, indi_id):
        individual = model.pop_find_individual(int(indi_id))
        # converts from unicode to dictionary
        fake_individual = []

        for i in individual:
            fake_individual.append(i['note'])

        #print fake_individual
        return render.fitness(title, indi_id, fake_individual)
    
    def POST(self, indi_id):
        """
        @TODO get all traits for the individual by gathering all the notes
        and user-notes for the indiviudal and storing in two lists. compute
        the euclidean distance between the two lists and set as fitness score
        for the individual

        @TODO oracle to decide what to do next
        """
        #model.pop_update_indi_fitness(int(indi_id), score)
        GA().fate(int(indi_id))

class SaveFitness:
    def POST(self, indi_id):
        """Updates the user-note in a single trait in an individual. This is information
        is used to find out what notes the user didn't like from the computer
        presented melody"""
        t_id = web.input()['trait_id']
        _note = web.input()['name']
        saved_traits = model.pop_find_trait(int(indi_id), int(t_id))
        model.pop_update_trait(saved_traits, {"$set": {"user_note":_note}})

class Terminate:
    def GET(self):
        """Render the terminate view and present the user with a list of save options"""
        return 'game over...'

    def POST(self):
        pass

if __name__ == "__main__":
   app.internalerror = web.debugerror
   app.run()


