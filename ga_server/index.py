import web
import json
import ast
import model
import ga
urls = (
        '/', 'Index',
        '/ga/population/(.*)', 'Population',
        '/ga/fitness', 'Fitness')

render = web.template.render('templates/', base='layout')
app = web.application(urls, globals())
title = 'GA Server'

class Index:
    def GET(self):
        # clear population collection
        model.pop_clear_conn()

        # parameters for calling the server
        route = 'spawn_pop'
        artist = 'Vivaldi'
        song = 'winter_allegro'
        num_indi = '4'
        num_traits = '2'
        size = '5000'
        nodes = '5'
        params = [route, artist, song, num_indi, num_traits, size, nodes]
        params = '/'.join(params)

        br = web.Browser()
        br.open(params)
        traits = json.loads(br.get_text())

        # add content to population collection
        for trait in traits:
            model.pop_save_individual(trait)

        # call pyevolve class to initialize everything
        return ga.init_ga(num_indi)

class Fitness:
    def GET(self):
        pass
    
if __name__ == "__main__":
   app.internalerror = web.debugerror
   app.run() 


