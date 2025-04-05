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
        self.semi_interactive = Config.SEMI_INTERACTIVE_MODE
        
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
        
        # Filter and sort results to find the best match
        candidates = results['results']
        
        # If we have a year, prioritize exact year matches
        if year:
            exact_year_matches = [
                movie for movie in candidates 
                if movie.get('release_date', '').startswith(year)
            ]
            if exact_year_matches:
                candidates = exact_year_matches
        
        # Look for exact title matches (case insensitive)
        title_lower = title.lower()
        exact_title_matches = [
            movie for movie in candidates
            if movie.get('title', '').lower() == title_lower
        ]
        if exact_title_matches:
            candidates = exact_title_matches
            
        # Sort remaining candidates by popularity
        candidates.sort(key=lambda x: x.get('popularity', 0), reverse=True)
        
        # If we have a single candidate or the top candidate is significantly more popular
        if len(candidates) == 1 or (len(candidates) > 1 and 
            candidates[0].get('popularity', 0) > candidates[1].get('popularity', 0) * 1.5):
            # Return top result without interactive selection
            return candidates[0]
        
        # If we have multiple good candidates with similar popularity, use interactive mode
        if self.interactive and len(candidates) > 1:
            selected = InteractiveUI.select_media_option(
                title=title,
                options=candidates,
                media_type="movie",
                filename=filename
            )
            return selected
            
        # If non-interactive or user chose the first result
        return candidates[0]
    
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
        
        results = self._make_request('search/tv', params)
        
        if not results or not results.get('results') or len(results['results']) == 0:
            return None
        
        # Filter and sort results to find the best match
        candidates = results['results']
        
        # If we have a year, prioritize exact year matches
        if year:
            exact_year_matches = [
                show for show in candidates 
                if show.get('first_air_date', '').startswith(year)
            ]
            if exact_year_matches:
                candidates = exact_year_matches
        
        # Look for exact title matches (case insensitive)
        title_lower = title.lower()
        exact_title_matches = [
            show for show in candidates
            if show.get('name', '').lower() == title_lower
        ]
        if exact_title_matches:
            candidates = exact_title_matches
            
        # Sort remaining candidates by popularity
        candidates.sort(key=lambda x: x.get('popularity', 0), reverse=True)
        
        # If we have a single candidate or the top candidate is significantly more popular
        if len(candidates) == 1 or (len(candidates) > 1 and 
            candidates[0].get('popularity', 0) > candidates[1].get('popularity', 0) * 1.5):
            # Return top result without interactive selection
            return candidates[0]
        
        # If we have multiple good candidates with similar popularity, use interactive mode
        if self.interactive and len(candidates) > 1:
            selected = InteractiveUI.select_media_option(
                title=title,
                options=candidates,
                media_type="tv",
                filename=filename
            )
            return selected
            
        # Return the first result if non-interactive or no clear winner
        return candidates[0]

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