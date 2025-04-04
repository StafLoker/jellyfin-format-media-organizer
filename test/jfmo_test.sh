#!/bin/bash

# Jellyfin Format Media Organizer - TEST script
# Only shows how files would be organized without making actual changes

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

# Function to simulate TV show processing
process_series() {
    file="$1"
    filename=$(basename "$file")
    
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
        
        # Format episode name (keep original extension)
        extension="${filename##*.}"
        new_filename="$series_name S${season_num}E${episode_num}${quality_suffix}.${extension}"
        
        # Show what would be done
        echo -e "${BLUE}TV SHOW DETECTED:${NC} $filename"
        echo -e "  ${YELLOW}→ Source:${NC} $file"
        echo -e "  ${YELLOW}→ Series name:${NC} $series_name$year_suffix"
        echo -e "  ${YELLOW}→ Season:${NC} $season_num"
        echo -e "  ${YELLOW}→ Episode:${NC} $episode_num"
        if [ -n "$quality" ]; then
            echo -e "  ${YELLOW}→ Quality:${NC} $quality"
        fi
        echo -e "  ${YELLOW}→ Destination:${NC} $season_dir/$new_filename"
        echo -e "  ${YELLOW}→ Action:${NC} Would create the structure if it doesn't exist and move the file"
        echo ""
    else
        echo -e "${RED}⚠️ Could not detect series pattern for:${NC} $filename"
        echo ""
    fi
}

# Function to simulate movie processing
process_movie() {
    file="$1"
    filename=$(basename "$file")
    
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
    
    # Show what would be done
    echo -e "${GREEN}MOVIE DETECTED:${NC} $filename"
    echo -e "  ${YELLOW}→ Source:${NC} $file"
    echo -e "  ${YELLOW}→ Clean title:${NC} $base_title"
    if [ -n "$year" ]; then
        echo -e "  ${YELLOW}→ Year:${NC} $year"
    fi
    if [ -n "$quality" ]; then
        echo -e "  ${YELLOW}→ Quality:${NC} $quality"
    fi
    echo -e "  ${YELLOW}→ Destination:${NC} $FILMS/$new_filename"
    echo -e "  ${YELLOW}→ Action:${NC} Would move the file"
    echo ""
}

# Special function for series directories like "La Casa de Papel 3"
process_special_series_dir() {
    dir="$1"
    dir_name=$(basename "$dir")
    
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
        
        echo -e "${BLUE}SPECIAL SERIES DETECTED:${NC} $dir_name"
        echo -e "  ${YELLOW}→ Series name:${NC} $series_name"
        echo -e "  ${YELLOW}→ Season:${NC} $season_num"
        if [ -n "$quality" ]; then
            echo -e "  ${YELLOW}→ Quality:${NC} $quality"
        fi
        echo -e "  ${YELLOW}→ Base destination:${NC} $season_dir"
        echo ""
        
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
            
            echo -e "  ${BLUE}Episode found:${NC} $filename"
            echo -e "    ${YELLOW}→ Source:${NC} $episode"
            echo -e "    ${YELLOW}→ Destination:${NC} $season_dir/$new_filename"
            echo ""
        done
        
        return 0
    fi
    
    return 1  # Not a special case
}

# Function to simulate series directory processing
process_series_dir() {
    dir="$1"
    dir_name=$(basename "$dir")
    
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
    
    echo -e "${BLUE}SERIES DIRECTORY DETECTED:${NC} $dir_name"
    echo -e "  ${YELLOW}→ Clean name:${NC} $clean_series$year_suffix"
    echo -e "  ${YELLOW}→ Base destination:${NC} $series_dir"
    echo ""
    
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
            
            # Format episode name
            new_filename="$clean_series S${season_num}E${episode_num}${quality_suffix}.${filename##*.}"
            
            # Show what would be done
            echo -e "  ${BLUE}Episode found:${NC} $filename"
            echo -e "    ${YELLOW}→ Source:${NC} $episode"
            echo -e "    ${YELLOW}→ Season:${NC} $season_num"
            echo -e "    ${YELLOW}→ Episode:${NC} $episode_num"
            if [ -n "$quality" ]; then
                echo -e "    ${YELLOW}→ Quality:${NC} $quality"
            fi
            echo -e "    ${YELLOW}→ Destination:${NC} $season_dir/$new_filename"
            echo -e "    ${YELLOW}→ Action:${NC} Would create Season $season_num structure if it doesn't exist and move the episode"
            echo ""
        else
            echo -e "  ${RED}⚠️ Could not detect episode pattern for:${NC} $filename"
            echo ""
        fi
    done
}

# Function to analyze and detect series patterns
detect_series_files() {
    # Group files by base name (before the SxxExx pattern)
    echo -e "${BLUE}Analyzing series patterns...${NC}"
    echo ""
    
    local series_patterns=()
    
    find "$DOWNLOADS" -maxdepth 1 -type f -name "*.mkv" -o -name "*.mp4" -o -name "*.avi" | while read file; do
        filename=$(basename "$file")
        # Extract series base name (before SxxExx)
        if [[ "$filename" =~ ^([^S]+)[S][0-9] ]]; then
            base_name="${BASH_REMATCH[1]}"
            # Remove last dot if it exists
            base_name=${base_name%.}
            
            # Check if we've already detected it
            if ! printf '%s\n' "${series_patterns[@]}" | grep -q "^$base_name$"; then
                series_patterns+=("$base_name")
                
                # Count how many episodes of this series
                count=$(find "$DOWNLOADS" -maxdepth 1 -type f -name "${base_name}*" | wc -l)
                
                # Get an example episode
                example=$(find "$DOWNLOADS" -maxdepth 1 -type f -name "${base_name}*" | head -1)
                example_name=$(basename "$example")
                
                # Clean name for display
                clean_base=$(clean_name "$base_name")
                year=$(get_year "$example_name")
                
                # Check for series with year-like names
                year_display=""
                if [ "$clean_base" = "$year" ]; then
                    # Don't show year in parentheses for series like "1923"
                    year_display=""
                elif [ -n "$year" ]; then
                    year_display=" ($year)"
                fi
                
                echo -e "${YELLOW}Series detected:${NC} $clean_base$year_display"
                echo -e "  ${BLUE}→ File pattern:${NC} ${base_name}*"
                echo -e "  ${BLUE}→ Example:${NC} $example_name"
                echo -e "  ${BLUE}→ Episode count:${NC} $count"
                echo -e "  ${BLUE}→ Destination:${NC} $SERIES/$clean_base$year_display/Season XX/"
                echo ""
            fi
        fi
    done
}

# Main function
main() {
    echo -e "${GREEN}🎬 JELLYFIN FORMAT MEDIA ORGANIZATION SIMULATION${NC}"
    echo -e "${YELLOW}This is a test that will NOT make real changes to files${NC}"
    echo -e "${YELLOW}It only shows how files would be organized${NC}"
    echo ""
    echo -e "${BLUE}📂 Downloads directory:${NC} $DOWNLOADS"
    echo -e "${BLUE}🎥 Movies directory:${NC} $FILMS"
    echo -e "${BLUE}📺 TV Shows directory:${NC} $SERIES"
    echo ""
    
    # Analyze series patterns first
    detect_series_files
    
    # Process files in downloads
    echo -e "${GREEN}=== ANALYZING INDIVIDUAL FILES ===${NC}"
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
    
    # Process directories (series)
    echo -e "${GREEN}=== ANALYZING SERIES DIRECTORIES ===${NC}"
    echo ""
    
    find "$DOWNLOADS" -maxdepth 1 -type d -not -path "$DOWNLOADS" -not -path "$DOWNLOADS/incomplete" | while read dir; do
        dir_name=$(basename "$dir")
        # Ignore "incomplete" directory
        if [ "$dir_name" != "incomplete" ]; then
            process_series_dir "$dir"
        fi
    done
    
    echo ""
    echo -e "${GREEN}✅ SIMULATION SUMMARY${NC}"
    echo -e "${YELLOW}If you run the real script:${NC}"
    echo -e "  - Necessary directory structures will be created"
    echo -e "  - Files will be moved to their destinations"
    echo -e "  - Format will be adjusted to Jellyfin recommendations:"
    echo -e "    ${BLUE}→ Movies:${NC} Title (Year) - [Quality].extension"
    echo -e "    ${BLUE}→ TV Shows:${NC} Series Name (Year)/Season XX/Series Name SxxExx - [Quality].extension"
    echo ""
    echo -e "${RED}IMPORTANT: This simulation has NOT made any real changes to your files.${NC}"
}

# Run main function
main