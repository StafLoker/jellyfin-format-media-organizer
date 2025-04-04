#!/bin/bash

# Jellyfin Format Media Organizer - Main script
# Reorganizes movies and TV shows according to the official Jellyfin format

# Colors for better visualization
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base directories
MEDIA_DIR="/data/media"
DOWNLOADS="$MEDIA_DIR/downloads"
FILMS="$MEDIA_DIR/films"
SERIES="$MEDIA_DIR/series"

# CONFIGURATION
# Change to true to move files instead of copying them
MOVE_FILES=false
# Change to true to generate a detailed log
VERBOSE=true
# Log file
LOG_FILE="/tmp/jfmo.log"

# Start log
echo "$(date) - Starting media organization" > "$LOG_FILE"

# Function to write to log
log() {
    if [ "$VERBOSE" = true ]; then
        echo "$(date) - $1" >> "$LOG_FILE"
    fi
}

# Function to clean names (remove special characters and prefixes)
clean_name() {
    # Remove prefixes like [NOOBDL], parentheses and suffixes like "LostFilm.TV"
    local name="$1"
    
    # Remove prefixes in brackets like [NOOBDL]
    name=$(echo "$name" | sed -E 's/\[[^]]*\]//g')
    
    # Remove suffixes like "- LostFilm.TV" or similar
    name=$(echo "$name" | sed -E 's/ ?- ?LostFilm\.TV.*//g')

    # Remove alternative titles in parentheses (e.g., "Расплата (The Accountant)")
    name=$(echo "$name" | sed -E 's/ ?\([^)]+\)//g')
    
    # Convert dots, hyphens and underscores to spaces
    name=$(echo "$name" | sed 's/\./\ /g' | sed 's/\_/\ /g' | sed 's/\-/\ /g' | sed 's/\*//' | sed 's/  / /g' | sed 's/^ //g' | sed 's/ $//g')
    
    # Remove quality tags like "2160p", "WEB-DL", "SDR", etc.
    name=$(echo "$name" | sed -E 's/ (480|720|1080|2160|4320)p//g' | sed -E 's/ (WEB|WEB-DL|WEBDL|HDR|SDR|BDRip).*//g')
    
    echo "$name"
}

# Function to get the year from a file
get_year() {
    # Look for year pattern (4 digits between 1900-2030)
    year=$(echo "$1" | grep -o -E '19[0-9]{2}|20[0-3][0-9]' | head -1)
    echo "$year"  # If no year, returns empty string
}

# Function to extract video quality
get_quality() {
    # Look for quality patterns like 1080p, 2160p, etc.
    quality=$(echo "$1" | grep -o -E '(480|720|1080|2160|4320)p' | head -1)
    
    if [ -n "$quality" ]; then
        echo "[${quality}]"
    else
        echo ""  # If no quality, returns empty string
    fi
}

# Function to detect series with various patterns
detect_season_episode() {
    filename="$1"
    
    # Pattern 1: S01E01
    if [[ "$filename" =~ [Ss]([0-9]{1,2})[Ee]([0-9]{1,2}) ]]; then
        season_num="${BASH_REMATCH[1]}"
        episode_num="${BASH_REMATCH[2]}"
        echo "$season_num $episode_num"
        return 0
    fi
    
    # Pattern 2: S01.E01
    if [[ "$filename" =~ [Ss]([0-9]{1,2})\.?[Ee]([0-9]{1,2}) ]]; then
        season_num="${BASH_REMATCH[1]}"
        episode_num="${BASH_REMATCH[2]}"
        echo "$season_num $episode_num"
        return 0
    fi
    
    # Pattern 3: Detect "La Casa de Papel 3" where 3 is the season
    if [[ "$filename" =~ Casa\ de\ Papel\ ([0-9]{1}) ]]; then
        season_num="${BASH_REMATCH[1]}"
        episode_num="00"  # No specific episode, use 00 as default
        echo "$season_num $episode_num"
        return 0
    fi
    
    return 1  # No season/episode pattern found
}

# Function to move or copy files
move_or_copy() {
    source_file="$1"
    dest_file="$2"
    
    # Create destination directory if it doesn't exist
    mkdir -p "$(dirname "$dest_file")"
    
    if [ "$MOVE_FILES" = true ]; then
        echo -e "${BLUE}Moving:${NC} $source_file -> $dest_file"
        mv "$source_file" "$dest_file"
        result=$?
        log "MOVING: $source_file -> $dest_file (result: $result)"
    else
        echo -e "${BLUE}Copying:${NC} $source_file -> $dest_file"
        cp "$source_file" "$dest_file"
        result=$?
        log "COPYING: $source_file -> $dest_file (result: $result)"
    fi
    
    if [ $result -eq 0 ]; then
        echo -e "${GREEN}✓ Success${NC}"
        return 0
    else
        echo -e "${RED}✗ Error${NC}"
        return 1
    fi
}

# Function to process TV shows
process_series() {
    file="$1"
    filename=$(basename "$file")
    
    log "Processing TV show: $filename"
    
    # Clean name and detect season/episode
    clean_title=$(clean_name "$filename")
    
    # Try to detect season and episode
    if season_episode=$(detect_season_episode "$filename"); then
        read season_num episode_num <<< "$season_episode"
        
        # Extract series name (before the SxxExx pattern)
        series_name=$(echo "$clean_title" | sed -E 's/S[0-9]{1,2}E[0-9]{1,2}.*$//' | sed 's/ $//')
        
        # Get year if it exists
        year=$(get_year "$filename")
        
        # Special check for series named with year-like numbers (like "1923")
        if [ "$series_name" = "$year" ]; then
            # If series name is the same as detected year, don't use the year suffix
            year=""
        fi
        
        year_suffix=""
        if [ -n "$year" ]; then
            year_suffix=" ($year)"
            # Remove year from series name if included
            series_name=$(echo "$series_name" | sed "s/ $year//g")
        fi
        
        # Format season number with leading zeros
        season_num=$(printf "%02d" $((10#$season_num)))
        
        # Get video quality
        quality=$(get_quality "$filename")
        quality_suffix=""
        if [ -n "$quality" ]; then
            quality_suffix=" - $quality"
        fi
        
        # Create series and season directories
        series_dir="$SERIES/$series_name$year_suffix"
        season_dir="$series_dir/Season $season_num"
        mkdir -p "$season_dir"
        
        # Format episode name (keep original extension)
        extension="${filename##*.}"
        new_filename="$series_name S${season_num}E${episode_num}${quality_suffix}.${extension}"
        
        # Move or copy file
        move_or_copy "$file" "$season_dir/$new_filename"
    else
        echo -e "${RED}⚠️ Could not detect series pattern for:${NC} $filename"
        log "ERROR: Could not detect series pattern for: $filename"
    fi
}

# Function to process movies
process_movie() {
    file="$1"
    filename=$(basename "$file")
    
    log "Processing movie: $filename"
    
    # Clean movie name
    filename_noext="${filename%.*}"
    clean_title=$(clean_name "$filename_noext")
    year=$(get_year "$filename")
    quality=$(get_quality "$filename")
    
    # Remove extension to get clean title
    base_title="${clean_title%.*}"
    
    # Remove year from title if it exists
    if [ -n "$year" ]; then
        base_title=$(echo "$base_title" | sed "s/ $year//g")
    fi
    
    # Format movie name with appropriate format
    extension="${filename##*.}"
    if [ -n "$year" ]; then
        if [ -n "$quality" ]; then
            new_filename="$base_title ($year) - $quality.$extension"
        else
            new_filename="$base_title ($year).$extension"
        fi
    else
        if [ -n "$quality" ]; then
            new_filename="$base_title - $quality.$extension"
        else
            new_filename="$base_title.$extension"
        fi
    fi
    
    # Create movies directory if it doesn't exist
    mkdir -p "$FILMS"
    
    # Move or copy file
    move_or_copy "$file" "$FILMS/$new_filename"
}

# Special function for series directories like "La Casa de Papel 3"
process_special_series_dir() {
    dir="$1"
    dir_name=$(basename "$dir")
    
    log "Processing special directory: $dir_name"
    
    # Special cases like "La Casa de Papel 3 - LostFilm.TV [1080p]"
    if [[ "$dir_name" =~ (La\ Casa\ de\ Papel)\ ([0-9]) ]]; then
        series_name="${BASH_REMATCH[1]}"
        season_num="${BASH_REMATCH[2]}"
        
        # Format season
        season_num=$(printf "%02d" $season_num)
        
        # Get quality if it exists
        quality=""
        quality_suffix=""
        if [[ "$dir_name" =~ \[([0-9]+p)\] ]]; then
            quality="[${BASH_REMATCH[1]}]"
            quality_suffix=" - $quality"
        fi
        
        # Create structure
        series_dir="$SERIES/$series_name"
        season_dir="$series_dir/Season $season_num"
        mkdir -p "$season_dir"
        
        echo -e "${BLUE}Special series detected:${NC} $dir_name"
        log "Special series detected: $dir_name"
        
        # Find files in directory
        find "$dir" -type f -name "*.mkv" -o -name "*.mp4" -o -name "*.avi" | while read episode; do
            filename=$(basename "$episode")
            episode_num="01"  # Assume episode 1 by default
            
            # Try to extract episode number if it exists in the name
            if [[ "$filename" =~ E([0-9]{2}) || "$filename" =~ ([0-9]{2})\.mkv ]]; then
                episode_num="${BASH_REMATCH[1]}"
            fi
            
            # Format final name
            new_filename="$series_name S${season_num}E${episode_num}${quality_suffix}.${filename##*.}"
            
            # Move or copy file
            move_or_copy "$episode" "$season_dir/$new_filename"
        done
        
        return 0
    fi
    
    return 1  # Not a special case
}

# Function to process series directories
process_series_dir() {
    dir="$1"
    dir_name=$(basename "$dir")
    
    log "Processing directory: $dir_name"
    
    # Check if it's a special case (like La Casa de Papel)
    if process_special_series_dir "$dir"; then
        return 0
    fi
    
    # General cleaning for other cases
    clean_series=$(clean_name "$dir_name")
    year=$(get_year "$dir_name")
    
    # Special check for series named with year-like numbers (like "1923")
    if [ "$clean_series" = "$year" ]; then
        # If series name is the same as detected year, don't use the year suffix
        year=""
    fi
    
    # Add year if it exists
    year_suffix=""
    if [ -n "$year" ]; then
        year_suffix=" ($year)"
        # Remove year from name if included
        clean_series=$(echo "$clean_series" | sed "s/ $year//g")
    fi
    
    # Create series directory
    series_dir="$SERIES/$clean_series$year_suffix"
    mkdir -p "$series_dir"
    
    echo -e "${BLUE}Processing series directory:${NC} $dir_name"
    
    # Find all episode files in the directory
    find "$dir" -type f -name "*.mkv" -o -name "*.mp4" -o -name "*.avi" | while read episode; do
        filename=$(basename "$episode")
        
        # Detect season and episode with multiple patterns
        if season_episode=$(detect_season_episode "$filename"); then
            read season_num episode_num <<< "$season_episode"
            
            # Format season number with leading zeros
            season_num=$(printf "%02d" $((10#$season_num)))
            
            # Get quality if it exists
            quality=$(get_quality "$filename")
            quality_suffix=""
            if [ -n "$quality" ]; then
                quality_suffix=" - $quality"
            fi
            
            # Create season directory
            season_dir="$series_dir/Season $season_num"
            mkdir -p "$season_dir"
            
            # Format episode name
            new_filename="$clean_series S${season_num}E${episode_num}${quality_suffix}.${filename##*.}"
            
            # Move or copy file
            move_or_copy "$episode" "$season_dir/$new_filename"
        else
            echo -e "${RED}⚠️ Could not detect episode pattern for:${NC} $filename"
            log "ERROR: Could not detect episode pattern for: $filename"
        fi
    done
}

# Main function
main() {
    echo -e "${GREEN}🎬 JELLYFIN FORMAT MEDIA ORGANIZER${NC}"
    if [ "$MOVE_FILES" = true ]; then
        echo -e "${YELLOW}MODE: MOVE${NC} - Files will be moved to their destinations"
    else
        echo -e "${YELLOW}MODE: COPY${NC} - Files will be copied to their destinations (originals will remain)"
    fi
    echo ""
    echo -e "${BLUE}📂 Downloads directory:${NC} $DOWNLOADS"
    echo -e "${BLUE}🎥 Movies directory:${NC} $FILMS"
    echo -e "${BLUE}📺 TV Shows directory:${NC} $SERIES"
    echo -e "${BLUE}📄 Log file:${NC} $LOG_FILE"
    echo ""
    
    # Verify that directories exist
    if [ ! -d "$DOWNLOADS" ]; then
        echo -e "${RED}Error: Downloads directory does not exist${NC}"
        exit 1
    fi
    
    log "Starting processing of individual files"
    echo -e "${GREEN}=== PROCESSING INDIVIDUAL FILES ===${NC}"
    echo ""
    
    # Process individual files (look for series first)
    find "$DOWNLOADS" -maxdepth 1 -type f \( -name "*.mkv" -o -name "*.mp4" -o -name "*.avi" \) | while read file; do
        filename=$(basename "$file")
        
        # Check if it's a series episode (SxxExx pattern)
        if season_episode=$(detect_season_episode "$filename"); then
            process_series "$file"
        else
            # If not a series, treat as movie
            process_movie "$file"
        fi
    done
    
    log "Starting directory processing"
    echo -e "${GREEN}=== PROCESSING SERIES DIRECTORIES ===${NC}"
    echo ""
    
    # Process directories (series)
    find "$DOWNLOADS" -maxdepth 1 -type d -not -path "$DOWNLOADS" -not -path "$DOWNLOADS/incomplete" | while read dir; do
        dir_name=$(basename "$dir")
        # Ignore "incomplete" directory
        if [ "$dir_name" != "incomplete" ]; then
            process_series_dir "$dir"
        fi
    done
    
    echo ""
    echo -e "${GREEN}✅ PROCESS COMPLETED${NC}"
    if [ "$MOVE_FILES" = false ]; then
        echo -e "${YELLOW}NOTE: Original files have not been deleted.${NC}"
        echo -e "${YELLOW}      To delete originals, modify the MOVE_FILES=true variable in the script.${NC}"
    fi
    
    log "Process completed"
    echo -e "${BLUE}A detailed log has been saved at: $LOG_FILE${NC}"
}

# Run main function
main