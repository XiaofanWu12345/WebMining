#Xiaofan Wu 903152422
import requests
from bs4 import BeautifulSoup as bs
import json
import time
import csv
import re

def scrape_all_movies(url):
    """Use the requests and beautifulsoup modules to extract the movie names and urls from
    an actor's IMDb webpage. Return a dictionary of all of the 
    extracted movies. The keys will be the movie titles, and the values 
    will be the corresponding urls (in string form) to that movie. The dictionary 
    will include all types of filmography the given actor acted in. This can include 
    TV shows, shorts, TV movies, and documentaries. It should not return filmography 
    in which the person is credited only with a role other than actor (director, writer, etc).
    
    Parameters:
    url: str -- the url for the imdb page of your chosen actor

    Return:
    all_movies: dict --
         where all_movies = {
                movie_name1: movie_url1,
                movie_name2: movie_url2,
                ...
                }
             and movie_name: str -- the name of a Kevin Bacon movie
             and movie_url: str -- the url address for that movie's page
    
    Usage Examples (note: not a complete test of all dictionary contents):
    >>> imdb_movies = scrape_all_movies('http://www.imdb.com/name/nm0000102/')
    >>> 'Apollo 13' in imdb_movies
    True
    >>> 'http://www.imdb.com/title/tt0327056' in [url[:35] for url in imdb_movies.values()]
    True
    >>> 'Captain America' in imdb_movies
    False
    """
    r = requests.get(url)
    s = bs(r.text, "html.parser")
    films = s.find('div', class_='filmo-category-section')
    return {f.text: 'http://www.imdb.com'+f.get('href') for f in films.find_all('a') if f.text!='post-production'}

def lookup_actor_name_by_id(actor_id):
    """Returns an actor's name by taking in the actor's actor_id using the 
    themoviedb.org's API and the requests module and the json module.
    
    Parameters:
    actor_id: int -- the themoviedb.org ID number of an actor

    Return:
    actor_name: str -- the name of the actor associated with the ID
    
    Usage Examples:
    >>> lookup_actor_name_by_id(4724)
    'Kevin Bacon'
    >>> lookup_actor_name_by_id(2963)
    'Nicolas Cage'
    """
    response = requests.get("https://api.themoviedb.org/3/person/{}?api_key={}&language=en-US".format(str(actor_id),API_KEY))
    return json.loads(response.text)['name']

def req_movies_for_actor(actor_id):
    """Looks up all the movies in which an actor with actor_id has been casted. 
    Returns the movies as a nested dictionary with the movie_id as the key, and 
    the name of the movie and the actor's ID as values in the nested dictionary.

    Parameters:
    actor_id: int -- the themoviedb.org ID number of an actor

    Return:
    movie_dict: dict --
        where movie_dict ={
            movie_id1: {
              "name": movie_name1,
              "parent": actor_id
            },
            movie_id2: {...},
            ...
            }
        and movie_id: int -- the themoviedb.org ID number of the movie
        and movie_name: str -- the name of the movie for the given ID

    Usage Examples:
    >>> movies = req_movies_for_actor(4724)
    >>> "Tremors" in [movie["name"] for movie in movies.values()]
    True
    >>> "Titanic" in [movie["name"] for movie in movies.values()]
    False
    >>> 4724 in [movie["parent"] for movie in movies.values()]
    True
    >>> 2963 in [movie["parent"] for movie in movies.values()]
    False
    """
    movies = requests.get("https://api.themoviedb.org/3/person/{}/movie_credits?api_key={}&language=en-US".format(str(actor_id),API_KEY))
    mlist = json.JSONDecoder().decode(movies.text)["cast"]
    movie_dict = {m["id"]:{"name":m["original_title"],"parent":actor_id} for m in mlist}
    return movie_dict

def req_actors_for_movie(movie_id):
    """Looks up all the cast members in the movie with movie_id. Returns the 
    cast as a nested dictionary with the cast member's ID as the key, and the 
    name of the cast member and the movie's ID as values in the nested 
    dictionary.
    
    Parameters:
    movie_id: int -- the themoviedb.org ID number of a movie

    Return:
    member_dict = dict --
        where member_dict = {
            member_id1: {
                "name": member_name1,
                "parent": movie_id
            },
            member_id2: {...},
            ...
            }
        and member_id: int -- the themoviedb.org ID number of an actor
        and member_name: str -- the name of the cast member for the given ID

    Usage Examples:
    >>> cast_members = req_actors_for_movie(9362)
    >>> 'Kevin Bacon' in [member["name"] for member in cast_members.values()]
    True
    >>> 'Nicolas Cage' in [member["name"] for member in cast_members.values()]
    False
    >>> 9362 in [member["parent"] for member in cast_members.values()]
    True
    >>> 597 in [member["parent"] for member in cast_members.values()]
    False
    """
    actors = requests.get("https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id),API_KEY))
    alist = json.JSONDecoder().decode(actors.text)["cast"]
    member_dict = {a["id"]:{"name":a["name"],"parent":movie_id} for a in alist}
    return member_dict

def one_deg_from_actor(from_actor_id):
    """Looks up all the co-stars for an actor with from_actor_id. Returns a 
    tuple with a nested dictionary of all the movies by id with their names and 
    parent actor (as in req_movies_for_actor) and a nested dictionary of all the
    costars by id with their names and parent movie (as in 
    req_actors_for_movie), excluding the from_actor_id themselves.
    Also, puts a delay before each request so that the script doesn't get an
    undesirable response from the API.

    Parameters:
    from_actor_id: int -- the themoviedb.org ID number of the actor to find one
      degree from

    Return:
    (movies, costars): tuple --
        where movies = {
            movie_id1:{
                "name": movie_name1,
                "parent": from_actor_id},
            movie_id2: {...},
            ...
            }
        and costars = {
            costar_id1:{
                "name": costar_name1,
                "parent": movie_id1},
            costar_id2: {...},
            ...
            }
    
    Usage Examples:
    >>> start_time = time.time()
    >>> bacon_movies, bacon_costars = one_deg_from_actor(4724) # this should take less than 60 secs
    >>> end_time = time.time() - start_time
    >>> end_time < 60
    True
    >>> len(bacon_movies)
    72
    >>> len(bacon_costars)
    1031
    >>> bacon_costars.get(4724, None) == None
    True
    """
    time.sleep(0.2)
    movies = req_movies_for_actor(from_actor_id)
    costars = {}
    for m_id in movies.keys():
        time.sleep(0.2)
        cdict = req_actors_for_movie(m_id)
        costars.update(cdict)
    del costars[from_actor_id]
    return (movies,costars)

def main(args):
    """Write your docstring here."""
    # Write your code here.
    a = True
    while a:
        if len(args) > 1:
            try:
                name = lookup_actor_name_by_id(int(args[1]))
                actor_id = int(args[1])
            except:
                print("ERROR: We don't recognize that id. They're obviously not connected to Kevin Bacon or anyone else for that matter. Please play again.")
                a = False
        else:
            reply = input("No actor chosen. Do you want to play one degree from the default chosen one, Kevin Bacon?")
            if reply.lower() == "yes":
                actor_id = 4724
            elif reply.lower() == "no":
                print("Goodbye, thanks for playing.")
                a = False 
                continue
        name = lookup_actor_name_by_id(actor_id) 
        clist = one_deg_from_actor(actor_id)[1].values()
        mlist = one_deg_from_actor(actor_id)[0].values()
        outlist = [[name,m["name"],c["name"]] for c in clist for m in mlist]
        if len(args)>2:            
            if not re.match(r"\.csv$",args[2]):
                print("ERROR: The output filename provided does not have a .csv extension. Please try again with a valid filename.")
                a = False
            elif not re.match(r"[A-Za-z0-9_\s@]+\.csv",args[2]):
                print("ERROR: Whoa, buddy! We can't write to files like that. Try again, and please try to keep it clean.")
                a = False
            with open(args[2],'w') as file:
                f = csv.writer(file)
                f.writerows(outlist)
        else:
            for i in outlist:
                print("{} > {} > {}".format(i[0],i[1],i[2]))
        a = False


print("If testing for Kevin Bacon, this should take less than 60 seconds.")
start_time = time.time()
if __name__ == "__main__":
    import sys
    main(sys.argv)
end_time = time.time() - start_time
print("Took {:.1f} seconds".format(end_time))
