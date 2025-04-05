#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TMDB (The Movie Database) integration for JFMO
"""

import requests
from typing import Dict, List, Optional, Tuple, Any
from ..config import Config
from ..utils import Logger, Colors
from ..utils.interactive_ui import InteractiveUI


class TMDBClient:
    """Client for The Movie Database API"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self, interactive=True):
        """
        Initialize the TMDB client
        
        Args:
            interactive (bool): Whether to allow user interaction for ambiguous results
        """
        self.api_key = Config.TMDB_API_KEY
        self.interactive = interactive and not Config.TEST_MODE
        
        if not self.api_key:
            print(f"{Colors.YELLOW}Warning: TMDB API key not configured. TMDB integration disabled.{Colors.NC}")
            Logger.warning("TMDB API key not configured. TMDB integration disabled.")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make a request to the TMDB API
        
        Args:
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            
        Returns:
            dict or None: Response data or None if request failed
        """
        if not self.api_key:
            return None
            
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Create headers with Bearer token
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json;charset=utf-8'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            Logger.error(f"TMDB API request failed: {str(e)}")
            return None
    
    def search_movie(self, title: str, year: Optional[str] = None, filename: Optional[str] = None) -> Optional[Dict]:
        """
        Search for a movie by title and optional year
        
        Args:
            title (str): Movie title to search for
            year (str, optional): Release year to filter by
            filename (str, optional): Original filename for interactive mode
            
        Returns:
            dict or None: Matching movie data or None if not found
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
        
        if not results or not results.get('results') or len(results['results']) == 0:
            return None
        
        # If we're in interactive mode and have multiple results, ask user to select
        if self.interactive and len(results['results']) > 1:
            selected = InteractiveUI.select_media_option(
                title=title,
                options=results['results'],
                media_type="movie",
                filename=filename
            )
            return selected
            
        # If non-interactive or user chose the first result
        if not year and len(results['results']) > 1:
            # Try to find an exact title match first
            title_lower = title.lower()
            for movie in results['results']:
                if movie.get('title', '').lower() == title_lower:
                    return movie
        
        # Return the first result
        return results['results'][0]
    
    def search_tv(self, title: str, year: Optional[str] = None, filename: Optional[str] = None) -> Optional[Dict]:
        """
        Search for a TV show by title and optional year
        
        Args:
            title (str): TV show title to search for
            year (str, optional): First air date year to filter by
            filename (str, optional): Original filename for interactive mode
            
        Returns:
            dict or None: Matching TV show data or None if not found
        """
        if not self.api_key:
            return None
            
        params = {
            'query': title,
            'include_adult': 'false',
            'language': 'en-US',
            'page': 1
        }
        
        # TMDB API doesn't support direct year filtering for TV shows
        # We'll filter results manually after getting them
        
        results = self._make_request('search/tv', params)
        
        if not results or not results.get('results') or len(results['results']) == 0:
            return None
        
        # If interactive mode and multiple results, ask user to select
        if self.interactive and len(results['results']) > 1:
            selected = InteractiveUI.select_media_option(
                title=title,
                options=results['results'],
                media_type="tv",
                filename=filename
            )
            return selected
            
        # Non-interactive mode or single result
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
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
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
    
    def get_tv_details(self, tv_id: int) -> Optional[Dict]:
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