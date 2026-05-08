import ast

from fastmcp import FastMCP
from langchain_community.utilities import SQLDatabase


def register_music_tools(mcp: FastMCP, db: SQLDatabase) -> None:
    @mcp.tool()
    def get_albums_by_artist(artist: str):
        """
        Get albums by an artist.
        
        Args:
            artist (str): Name of the artist.

        Returns:
            list[dict]: A list of albums that match the artist name.
        """
        result = db.run(
            f"""
            SELECT Album.Title, Artist.Name 
            FROM Album 
            JOIN Artist ON Album.ArtistId = Artist.ArtistId 
            WHERE Artist.Name LIKE '%{artist}%';
            """,
            include_columns=True
        )
        if not result:
            return []
        return ast.literal_eval(result)

    @mcp.tool()
    def get_tracks_by_artist(artist: str):
        """
        Get all songs for customer using artist name.
        
        Args:
            artist (str): Name of the artist.

        Returns:
            list[dict]: A list of songs that match the artist name.
        """
        result = db.run(
            f"""
            SELECT Track.Name as SongName, Artist.Name as ArtistName 
            FROM Album 
            LEFT JOIN Artist ON Album.ArtistId = Artist.ArtistId 
            LEFT JOIN Track ON Track.AlbumId = Album.AlbumId 
            WHERE Artist.Name LIKE '%{artist}%';
            """,
            include_columns=True
        )
        if not result:
            return []
        return ast.literal_eval(result)

    @mcp.tool()
    def get_songs_by_genre(genre: str):
        """
        Fetch songs from the database that match a specific genre.
        
        Args:
            genre (str): The genre of the songs to fetch.
        
        Returns:
            list[dict]: A list of songs that match the specified genre.
        """
        genre_id_query = f"SELECT GenreId FROM Genre WHERE Name LIKE '%{genre}%'"
        genre_ids = db.run(genre_id_query)

        if not genre_ids:
            return []

        genre_ids = ast.literal_eval(genre_ids)
        genre_id_list = ", ".join(str(gid[0]) for gid in genre_ids)

        songs_query = f"""
            SELECT Track.Name as SongName, Artist.Name as ArtistName
            FROM Track
            LEFT JOIN Album ON Track.AlbumId = Album.AlbumId
            LEFT JOIN Artist ON Album.ArtistId = Artist.ArtistId
            WHERE Track.GenreId IN ({genre_id_list})
            LIMIT 8;
        """

        songs = db.run(songs_query, include_columns=True)

        if not songs:
            return []
        return ast.literal_eval(songs)

    @mcp.tool()
    def check_for_songs(song_title: str):
        """
        Check if a song exists by its name.
        
        Args:
            song_title (str): Name of the song.

        Returns:
            list[dict]: A list of songs that match the song name.
        """
        result = db.run(
            f"""
            SELECT * FROM Track WHERE Name LIKE '%{song_title}%';
            """,
            include_columns=True
        )
        if not result:
            return []
        return ast.literal_eval(result)