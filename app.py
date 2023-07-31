import pickle
import streamlit as st
import requests

movies=pickle.load(open('movie_dic.pkl','rb'))
similarity=pickle.load(open('similarty.pkl','rb'))

st.set_page_config(
    page_title="Movie Recommender System App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_file_contents(filename):
    """ Given a filename,
        return the contents of that file
    """
    try:
        with open(filename, 'r') as f:
            # It's assumed our file contains a single line,
            # with our API key
            return f.read().strip()
    except FileNotFoundError:
        print("'%s' file not found" % filename)

filename='apikey'  
api_key = get_file_contents(filename)

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key={}".format(int(movie_id),api_key)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + str(poster_path)
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names,recommended_movie_posters


def movie_info(movie_name):
    movie_id = movies[movies['title'] == movie_name].movie_id
    path =fetch_poster(int(movie_id))
    return path

def movie_data(movie_name):
    movie_id = movies[movies['title'] == movie_name].movie_id
    url = "https://api.themoviedb.org/3/movie/{}?api_key={}".format(int(movie_id),api_key)
    data = requests.get(url)
    data = data.json()

    #budget
    budget=data['budget']
    #release date
    release_date=data['release_date']
    #revenue
    revenue=data['revenue']
    #rating
    rating=str(data['vote_average'])+" / "+str(data['vote_count'])
    #geners
    genres = " "
    for i in range(len(data['genres'])):
        genres += data['genres'][i]['name'] + ", "

    #overview
    overview=data['overview']
    #runtime
    runtime=str(data['runtime'])+ " minutes"

    url_credict = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(int(movie_id),api_key)
    crew_data = requests.get(url_credict)
    crew_data = crew_data.json()
    #director name
    for i in range(len(crew_data['crew'])):
        director_name=''
        if crew_data['crew'][i]['known_for_department'] == 'Directing' and crew_data['crew'][i]['job'] == 'Director':
            director_name = crew_data['crew'][i]['name']
            break

    return overview,rating,genres,director_name,release_date,runtime,revenue,budget

def actor_data(movie_name):
    movie_id = movies[movies['title'] == movie_name].movie_id
    url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(int(movie_id),api_key)
    actor_data = requests.get(url)
    actor_data = actor_data.json()
    actor_name=[]
    actor_poster_path=[]
    count = 0
    for i in range(len(actor_data['cast'])):
        if actor_data['cast'][i]['known_for_department'] == 'Acting' and count < 6:
            actor_name.append(actor_data['cast'][i]['original_name'])
            actor_poster_path.append("https://image.tmdb.org/t/p/w500/" + str(actor_data['cast'][i]['profile_path']))
            count+=1
    return actor_name,actor_poster_path


st.header('Movie Recommender System')

st.markdown(
    """
    <style>
    .reportview-container {
        background: url("url_goes_here")
    }
   .sidebar .sidebar-content {
        background: url("url_goes_here")
    }
    </style>
    """,
    unsafe_allow_html=True
)

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    st.markdown("<h1 style='text-align: center; ;color: white;'> Movie Info</h1>", unsafe_allow_html=True)
    recommended_movie_names,recommended_movie_posters = recommend(selected_movie)
    with st.container():
        col6, col7 = st.columns(2)
        with col6:
            path=movie_info(selected_movie)
            st.image(path,width=350,)
        with col7:
            name='Movie Name\t\t\t\t:\t{}'.format(selected_movie)
            st.markdown('<p style="font-family:sans-serif; font-size: 22px;">{}</p>'.format(name),
                        unsafe_allow_html=True)

            overview, rating, genres, director_name, release_date, runtime, revenue, budget = movie_data(selected_movie)

            overview = 'Overview\t:\t{}'.format(overview)
            st.markdown('<p style="font-family:sans-serif;font-size: 22px;">{}</p>'.format(overview),
                        unsafe_allow_html=True)

            rating = 'Rating\t:\t{}'.format(rating)
            st.markdown('<p style="font-family:sans-serif; font-size: 22px;">{}</p>'.format(rating),
                        unsafe_allow_html=True)

            genres = 'Genres\t:\t{}'.format(genres)
            st.markdown('<p style="font-family:sans-serif;  font-size: 22px;">{}</p>'.format(genres),
                        unsafe_allow_html=True)

            director_name = 'Director Name\t:\t{}'.format(director_name)
            st.markdown('<p style="font-family:sans-serif;  font-size: 22px;">{}</p>'.format(director_name),
                        unsafe_allow_html=True)

            release_date = 'Release Date\t:\t{}'.format(release_date)
            st.markdown('<p style="font-family:sans-serif;  font-size: 22px;">{}</p>'.format(release_date),
                        unsafe_allow_html=True)

            budget = 'Budget\t:\t{}'.format(budget)
            st.markdown('<p style="font-family:sans-serif; font-size: 22px;">{}</p>'.format(budget),
                        unsafe_allow_html=True)


    st.markdown("<h1 style='text-align: center; ;color: white;'> Top Actor</h1>", unsafe_allow_html=True)

    actor_name, actor_poster_path = actor_data(selected_movie)
    col11, col12, col13, col14, col15 = st.columns(5)
    with col11:
        st.text(actor_name[0])
        st.image(actor_poster_path[0])
    with col12:
        st.text(actor_name[1])
        st.image(actor_poster_path[1])

    with col13:
        st.text(actor_name[2])
        st.image(actor_poster_path[2])
    with col14:
        st.text(actor_name[3])
        st.image(actor_poster_path[3])
    with col15:
        st.text(actor_name[4])
        st.image(actor_poster_path[4])

    st.markdown("<h1 style='text-align: center; ;color: white;'>Top Recommended Movies</h1>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommended_movie_names[0])
        st.image(recommended_movie_posters[0])
    with col2:
        st.text(recommended_movie_names[1])
        st.image(recommended_movie_posters[1])

    with col3:
        st.text(recommended_movie_names[2])
        st.image(recommended_movie_posters[2])
    with col4:
        st.text(recommended_movie_names[3])
        st.image(recommended_movie_posters[3])
    with col5:
        st.text(recommended_movie_names[4])
        st.image(recommended_movie_posters[4])




