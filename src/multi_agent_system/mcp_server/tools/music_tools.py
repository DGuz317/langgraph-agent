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
    def get_songs_by_genre(genre: str) -> list[dict]:
        """
        Fetch songs that match a specific genre.
        """
        genre_query = """
            SELECT GenreId
            FROM Genre
            WHERE Name LIKE :genre;
        """

        genre_result = db.run(
            genre_query,
            parameters={"genre": f"%{genre}%"},
        )

        if not genre_result:
            return []

        genre_ids = ast.literal_eval(genre_result)
        genre_id_values = [str(row[0]) for row in genre_ids]

        if not genre_id_values:
            return []

        songs_query = f"""
            SELECT Track.Name AS SongName, Artist.Name AS ArtistName
            FROM Track
            LEFT JOIN Album ON Track.AlbumId = Album.AlbumId
            LEFT JOIN Artist ON Album.ArtistId = Artist.ArtistId
            WHERE Track.GenreId IN ({",".join(genre_id_values)})
            LIMIT 8;
        """

        songs = db.run(songs_query, include_columns=True)

        if not songs:
            return []

        return ast.literal_eval(songs)

    @mcp.tool()
    def check_for_songs(song_title: str) -> list[dict]:
        """
        Check whether a song exists by title.
        """
        query = """
            SELECT *
            FROM Track
            WHERE Name LIKE :song_title;
        """

        result = db.run(
            query,
            parameters={"song_title": f"%{song_title}%"},
            include_columns=True,
        )

        if not result:
            return []

        return ast.literal_eval(result)