#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TMDB (The Movie Database) integration for JFMO
"""

import os
import requests
import json
from ..config import Config
from ..utils import Logger, Colors


class TMDBClient:
    """Client for The Movie Database API"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self):
        """Initialize the TMDB client"""
        self.api_key = Config.TMDB_API_KEY
        if not self.api_key:
            print(f"{Colors.YELLOW}Warning: TMDB API key not configured. TMDB integration disabled.{Colors.NC}")
            Logger.warning("TMDB API key not configured. TMDB integration disabled.")
    
    def _make_request(self, endpoint, params=None):
        """Make a request to the TMDB API"""
        if not self.api_key:
            return None
            
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Add API key to parameters
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            Logger.error(f"TMDB API request failed: {str(e)}")
            return None
    
    def search_movie(self, title, year=None):
        """
        Search for a movie by title and optional year
        
        Args:
            title (str): Movie title to search for
            year (str, optional): Release year to filter by
            
        Returns:
            dict or None: First matching movie result or None if not found
        """
        if not self.api_key:
            return None
            
        params = {
            'query': title,
            'include_adult': 'false',
            'language': 'en-US',
            'page': 1
        }
        
        if year:
            params['year'] = year
        
        results = self._make_request('search/movie', params)
        
        if results and results.get('results') and len(results['results']) > 0:
            # If we have multiple results and a year, try to filter by year
            if not year and len(results['results']) > 1:
                # Try to find an exact title match first
                title_lower = title.lower()
                for movie in results['results']:
                    if movie.get('title', '').lower() == title_lower:
                        return movie
            
            # Return the first result
            return results['results'][0]
        
        return None
    
    def search_tv(self, title, year=None):
        """
        Search for a TV show by title and optional year
        
        Args:
            title (str): TV show title to search for
            year (str, optional): First air date year to filter by
            
        Returns:
            dict or None: First matching TV show result or None if not found
        """
        if not self.api_key:
            return None
            
        params = {
            'query': title,
            'include_adult': 'false',
            'language': 'en-US',
            'page': 1
        }
        
        # Note: TMDB doesn't support direct year filtering for TV shows via API parameter
        # We'll filter results manually after getting them
        
        results = self._make_request('search/tv', params)
        
        if results and results.get('results') and len(results['results']) > 0:
            if year and len(results['results']) > 1:
                # Try to find a show that matches the year
                for show in results['results']:
                    first_air_date = show.get('first_air_date', '')
                    if first_air_date and first_air_date.startswith(year):
                        return show
                
                # If no exact year match, try to find an exact title match
                title_lower = title.lower()
                for show in results['results']:
                    if show.get('name', '').lower() == title_lower:
                        return show
            
            # Return the first result if no specific match found
            return results['results'][0]
        
        return None
    
    def get_movie_details(self, movie_id):
        """
        Get detailed information about a specific movie
        
        Args:
            movie_id (int): TMDB movie ID
            
        Returns:
            dict or None: Movie details or None if not found
        """
        if not self.api_key:
            return None
            
        return self._make_request(f'movie/{movie_id}')
    
    def get_tv_details(self, tv_id):
        """
        Get detailed information about a specific TV show
        
        Args:
            tv_id (int): TMDB TV show ID
            
        Returns:
            dict or None: TV show details or None if not found
        """
        if not self.api_key:
            return None
            
        return self._make_request(f'tv/{tv_id}')