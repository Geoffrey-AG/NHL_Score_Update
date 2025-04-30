###--------------------------------------------------------------------------------------------------------------###
### Name: BUFFALO SABRES SCORE BOARD                                                                             ###
### Date: 02-17-2025                                                                                             ###
### Updated: 04-17-2025                                                                                          ###
### Author: GEOFFREY A. GOMLAK                                                                                   ###
### Version: 4.4                                                                                                ###
### Purpouse: KEEPS LIVE SCORE AND TIME OF BUFFALO SABRES GAMES. PLAYS VIDEOS AND SOUND DURING MAJOR GAME EVENTS ###
###--------------------------------------------------------------------------------------------------------------###

import pygame
import time 
import requests
import imageio_ffmpeg
import os
import tkinter as tk
import time
import pyttsx3
from moviepy.editor import VideoFileClip
from datetime import datetime


#Constants
date = datetime.now().strftime('%Y-%m-%d')
api_url = (f'https://api-web.nhle.com/v1/score/{date}') #NHL API
team_id = 7 #Buffalo Sabres ID
video_transistion = "/home/sabre/venv/lib/python3.12/site-packages/Untitled Folder/Transition.mov"
sabre_goal = "/home/sabre/venv/lib/python3.12/site-packages/Untitled Folder/goal.mov"
enemy_goal = "/home/sabre/venv/lib/python3.12/site-packages/Untitled Folder/sad.mov"
pre_game = "/home/sabre/venv/lib/python3.12/site-packages/Untitled Folder/start.mp4"
no_goal = "/home/sabre/venv/lib/python3.12/site-packages/Untitled Folder/no_goal.mov"
win = "/home/sabre/venv/lib/python3.12/site-packages/Untitled Folder/Sabres_Win.mp4"
loss = "/home/sabre/venv/lib/python3.12/site-packages/Untitled Folder/Sad.mp3"
period_end = "/home/sabre/venv/lib/python3.12/site-packages/Untitled Folder/period_end.mp3"
background_image = "/home/sabre/venv/lib/python3.12/site-packages/Untitled Folder/score.jpg"
screen_width = 1980
screen_hight = 1080
font_size_xl = pygame.font.SysFont('Arial', 85)
font_size_large = pygame.font.SysFont('Arial', 80)
font_size_medium = pygame.font.SysFont('Arial', 50)
font_size_small = pygame.font.SysFont('Arial', 36)
font_size_norm = 56
text_color = (0, 0, 0) #Black
sync_delay = 5 #Delay to sync to live feed
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)
logo_size = (150, 150)
from datetime import datetime, time as dt_time
import time  # for sleep

#Home Attistant
#home_assistant_api = "link"
#token = "12345"
#goal_light = "lights"

#Home Assistant Client
#ha_client = Client(home_assistant_api, token)

#Starting Pygame
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_hight))
pygame.display.set_caption("Score Board")
font = pygame.font.Font(None, font_size_norm)
clock = pygame.time.Clock()

#Load Images
def load_image(backgorund_image, size=None):
    if not os.path.isfile(backgorund_image):
        print('File Not Found:')
        return pygame.Surface((100, 100))

    try:
        image = pygame.image.load(backgorund_image).convert_alpha()
        return pygame.transform.scale(image, size) if size else image
    except Exception as e:
        print(f"Error loading image '{backgorund_image}': {e}")
        return pygame.Surface(size if size else (100, 100))

background = load_image(background_image, (screen_width, screen_hight))

#Checks fo FFmpeg
try: 
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"FFmpeg detected at: {ffmpeg_path}")
except Exception as e:
     print(f"Error detecting FFmpeg: {e}\nMake sure FFmpeg is installed system-wide with 'sudo apt install ffmpeg'.")

#Playing Video With Sound Using Moviepy
def play_video(sabre_goal): 
    try:
        clip = VideoFileClip(sabre_goal)
        clip.preview(fullscreen=True)
        clip.close()
    except Exception as e:
        print(f"Error....: {e}")

#Plays Audio Files
def play_sound(win):
    if not os.path.isfile(win):
        print(f"Sound file not found: {win}")
        return
    try:
        pygame.mixer.music.load(win)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Wait until the sound finishes playing
    except pygame.error as e:
         print(f"Error playing sound '{win}': {e}")
    

#Get Live Game Data
def get_game_data(team_id):
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        games = data.get('games')
        if not games:
            print("No games found for the given date.")
            return None
        for game in games:
            if game.get('homeTeam', {}).get('id') == team_id or game.get('awayTeam', {}).get('id') == team_id:
                return game
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    
    except response.status_code != 200:
        print(f"Error: NHL API responded with {response.status_code}")
        return None
            
    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        return None

#Goal Lights
#def lights():
#    try:
#        ha_client.services.call("light", "turn_on", {"entity_id": goal_light, "brightness": 255, "color_name": "red"})
#        print("Lights turned on!")
#    except Exception as e:
#        print(f"Failed to turn on lights: {e}")

#Creats Score Board
def load_image(image_path, size=(50, 50)):
    """Load and scale an image from a file."""
    try:
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, size)  # Scale the image to the desired size
        return image
    except pygame.error as e:
        print(f"Error loading image: {e}")
        return None


#Creats Live Score Board
def draw_live_score(game, background_image):
    global power_play_timers

    """Render the live score, period, time, power play status, and team logos with a custom background in scoreboard style."""
    # Load and display the background image
    background = pygame.image.load(background_image)
    background = pygame.transform.scale(background, (screen_width, screen_hight))  # Scale to fit screen size
    screen.blit(background, (0, 0))  # Draw the background at position (0, 0)

    period = game.get('periodDescriptor', {}).get('number', "-")
    time_remaining = game.get('clock', {}).get('timeRemaining', "00:00")
    home_team = game.get('homeTeam', {}).get('abbrev', "HOME")
    away_team = game.get('awayTeam', {}).get('abbrev', "AWAY")
    home_score = game.get('homeTeam', {}).get('score', 0)
    away_score = game.get('awayTeam', {}).get('score', 0)

    
    # Load team logos based on the team abbreviations
    home_logo = load_image(f"logos/{home_team}.png", size=(550, 550))
    away_logo = load_image(f"logos/{away_team}.png", size=(550, 550))

    # Fonts for different sections
    period_time_font = pygame.font.SysFont('Arial', 40)  # Medium font for period/time
    small_font = pygame.font.SysFont('Arial', 30)  # Small font for power play info

    #suffix = get_period_suffix(period)
    period_text = period_time_font.render(f"{period}", True, (225, 225, 225))
    time_text = period_time_font.render(time_remaining, True, (225, 225, 225))


    # Define positions for layout
    header_y = 300  # Distance from top for team logos/names
    score_y = 150  # Distance from top for scores
    period_time_y = 920  # Distance from top for period/time info
    power_play_y = 320  # Distance from top for power play status
    logo_name_gap = 680 # Gap between logo and name

    #Displays Shots on Goal
    home_shots = game.get('homeTeam', {}).get('sog', 0)
    away_shots = game.get('awayTeam', {}).get('sog', 0)

    font_size_medium.set_bold(True)
    home_shots_text = font_size_medium.render(f"SOG: {home_shots}", True, (225, 225, 225))
    away_shots_text = font_size_medium.render(f"SOG: {away_shots}", True, (0, 0, 0))
    font_size_medium.set_bold(False)

    screen.blit(home_shots_text, (600, 940))  
    screen.blit(away_shots_text, (screen_width - away_shots_text.get_width() - 600, 940))

    # Display team names and logos
    if home_logo:
        screen.blit(home_logo, (screen_width // 5 - home_logo.get_width() // 2, header_y))
    if away_logo:
        screen.blit(away_logo, (screen_width * 3 // 4 - away_logo.get_width() // 5, header_y))

    # Display team names in large font
    font_size_xl.set_bold(True)
    home_team_text = font_size_xl.render(home_team, True, (255, 255, 255))
    away_team_text = font_size_xl.render(away_team, True, (0, 0, 0))
    font_size_xl.set_bold(False)

    # Adjust Y-coordinates for team names using the gap
    screen.blit(home_team_text, (screen_width // 4 - home_team_text.get_width() // 2, header_y + home_logo.get_height() - logo_name_gap))
    screen.blit(away_team_text, (screen_width * 3 // 4 - away_team_text.get_width() // 2, header_y + away_logo.get_height() - logo_name_gap))

    # Display scores using number images
    def display_score(score, x_offset, y_offset):
        score_str = str(score)
        y_pos = y_offset
        for digit in score_str:
            digit_image = load_image(f"numbers/{digit}.png", size=(200, 200))  # Load digit image
            if digit_image:
                screen.blit(digit_image, (x_offset, y_pos))  # Place digit at (x_offset, y_pos)
                y_pos += digit_image.get_height() + 10  # Move down for the next digit (5px gap)

    # Increase the gap between team logos and scores to avoid overlap
    home_score_x_offset = screen_width // 4 + 230 # Position after home logo and team name
    away_score_x_offset = screen_width * 3 // 4 - 360  # Position after away logo and team name

    home_score_y_offset = 420  # Start Y-position for vertical home score
    away_score_y_offset = 420  # Start Y-position for vertical away score
    
    display_score(home_score, home_score_x_offset, home_score_y_offset)
    display_score(away_score, away_score_x_offset, away_score_y_offset)


    # Display period and time info (centered)
    screen.blit(time_text, ((screen_width - time_text.get_width()) // 2, period_time_y))
    screen.blit(period_text, ((screen_width - period_text.get_width()) // 2, period_time_y + time_text.get_height() + 10)) 


    # Update the display
    pygame.display.flip()

#Announce Goal
def announce_goal(game):
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 130)

    if 'goals' in game and game['goals']:
        last_goal = game['goals'][-1]

        # Only continue if Buffalo scored
        if last_goal.get('teamAbbrev') != 'BUF':
            return  # Not a Buffalo goal, skip announcement

        scorer_id = last_goal.get('playerId')
        goal_scorer = last_goal.get('firstName', {}).get('default', '') + ' ' + \
                      last_goal.get('lastName', {}).get('default', 'Unknown')
        time_in_period = last_goal.get('timeInPeriod', 'Unknown')

        # Get assists list (may be empty)
        assists = last_goal.get('assists', [])
        assist_names = []
        for assist in assists:
            assist_name = assist.get('name', {}).get('default', 'Unknown')
            assist_names.append(assist_name)

        # Get jersey number by matching with rosterSpots
        jersey_number = 'Unknown'
        if 'rosterSpots' in game:
            for player in game['rosterSpots']:
                if player.get('playerId') == scorer_id:
                    jersey_number = str(player.get('sweaterNumber', 'Unknown'))
                    break

        # Build announcement
        text = f"Buffalo Goal! Scored by, {goal_scorer}, at {time_in_period}"
        if assist_names:
            if len(assist_names) == 1:
                text += f", assisted by {assist_names[0]}"
            else:
                text += f", assisted by {assist_names[0]} and {assist_names[1]}"

        print(text)
        tts_engine.say(text)
        tts_engine.runAndWait()


# Set target transition time (5:00 PM)
target_time = dt_time(hour=19, minute=30) #17:00 (5:00pm)

def play_pregame_videos():
    transitioned = False
    while not transitioned:
        now = datetime.now().time()
        game_data = get_game_data(team_id)
        game_state = game_data.get('gameState') if game_data else None

        print(f"[{datetime.now()}] Game state: {game_state}, Time: {now.strftime('%H:%M:%S')}")

        if game_state in ["LIVE", "CRIT"]:
            print("Game is LIVE or about to start.")
            play_video(video_transistion)
            transitioned = True

        elif now >= target_time:
            print("It's 5:00 PM or later — playing transition video.")
            play_video(video_transistion)
            transitioned = True

        elif game_state in ["FUT", "PRE"]:
            print("Still waiting... game not live and not yet 5:00 PM.")
            play_video(pre_game)  # Optional: looped pre-game content        

        time.sleep(3)  # Slightly longer interval to avoid spamming the API
    
    # Handle events (like quitting)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

#Tracks Live Data
def track_scores():
    play_pregame_videos()  # Play pre-game and transition videos

    last_period = 0
    last_home_score, last_away_score = 0, 0
    overtime_detected = False
    shootout_detected = False

    while True:
        game = get_game_data(team_id)
        if not game:
            time.sleep(sync_delay)
            continue

        period = game.get('periodDescriptor', {}).get('number', 0)
        period_type = game.get('periodDescriptor', {}).get('periodType', "")
        home_score = game.get('homeTeam', {}).get('score', 0)
        away_score = game.get('awayTeam', {}).get('score', 0)
        time_remainings = game.get('clock', {}).get('timeRemaining', "00:00")

        # Detect period end
        if time_remainings == "00:00" and period != last_period:
            print(f"End of Period {period}!")
            if period == 1:
                play_sound(period_end)  # Custom sound for end of period 1
            elif period == 2:
                play_sound(period_end)  # Custom sound for end of period 2
            last_period = period  # Update last recorded period
        
        # Detect overtime start
        if period_type == "OVERTIME" and not overtime_detected:
            print("Overtime has started!")
            overtime_detected = True  # Mark OT as started

        # Detect shootout start
        if period_type == "SHOOTOUT" and not shootout_detected:
            print("Shootout has started!")
            shootout_detected = True  # Mark SO as started

       # Track Sabres goals (regulation, OT, or SO)
        if game['homeTeam']['id'] == team_id and home_score > last_home_score:
            print("Sabres scored!")
            play_video(sabre_goal)
            announce_goal(game)

        elif game['awayTeam']['id'] == team_id and away_score > last_away_score:
            print("Sabres scored!")
            play_video(sabre_goal)
            announce_goal(game)

        # Enemy score detection (any period)
        elif home_score > last_home_score or away_score > last_away_score:
            print("Enemy scored!")
        
        # Disallowed Goal Detection
        elif home_score < last_home_score or away_score < last_away_score:
            print("Disallowed goal detected!")
            play_video(no_goal)
        
        last_home_score, last_away_score = home_score, away_score

        # Final Game Outcome
        if game.get('gameState') == "FINAL":
            is_home_team = game['homeTeam']['id'] == team_id
            is_winner = (is_home_team and home_score > away_score) or (not is_home_team and away_score > home_score)

            if is_winner:
                play_video(win)
                time.sleep(20)
                exit()
            else:
                play_sound(loss)
                time.sleep(20)
                exit()
            break

        draw_live_score(game, background_image)  # Drawing the live score after the transition
        time.sleep(sync_delay)

            
# Tests for individual video and sound functions
def test_pre_game_video():
    print('Test Pre-game video:')
    play_video(pre_game)

def test_transition_video():
    print('Test transition video:')
    play_video(video_transistion)

def test_team_goal():
    print('Test team goal:')
    play_video(sabre_goal)

def test_enemy_goal():
    print('Test enemy goal:')
    play_video(enemy_goal)

def test_disallowed_goal():
    print('Test disallowed goal:')
    play_video(no_goal)

def test_end_of_period_sound():
    print('Test end of period sound:')
    play_sound(period_end)

def test_team_win_sound():
    print('Test team win video:')
    play_video(win)

def test_loss_sound():
    print('Test loss sound:')
    play_sound(loss)

def test_live_clock():
    print('Test Live clock:')
    
    # Dummy game state with power play and skater counts
    dummy_game = {
        'homeTeam': {
            'abbrev': 'BUF',
            'score': 1,
            'id': team_id,
            'sog': 18,
        },
        'awayTeam': {
            'abbrev': 'PHI',
            'score': 0,
            'sog': 18,
        },
        'periodDescriptor': {'number': '1'},
        'clock': {'timeRemaining': '2:00'}
    }

    # Simulate 10 clock updates
    for _ in range(10):
        # Draw live score with updated power play state
        draw_live_score(dummy_game, background_image)
        
        # Simulate real-time delay
        time.sleep(2)

def exit_button():
    exit()

def open_test_window():
    """Opens a new window for test function selection."""
    test_window = tk.Toplevel()
    test_window.title("Test Functions")
    test_window.geometry("400x520")

    tk.Label(test_window, text="Test Functions", font=("Arial", 16)).pack(pady=20)

    # Test buttons in the new window
    tk.Button(test_window, text="Test Pre-game Video", font=("Arial", 12), command=test_pre_game_video).pack(pady=5)
    tk.Button(test_window, text="Test Transition Video", font=("Arial", 12), command=test_transition_video).pack(pady=5)
    tk.Button(test_window, text="Test Team Goal", font=("Arial", 12), command=test_team_goal).pack(pady=5)
    tk.Button(test_window, text="Test Announcement", font=("Arial", 12), command=announce_goal).pack(pady=5)
    tk.Button(test_window, text="Test Enemy Goal", font=("Arial", 12), command=test_enemy_goal).pack(pady=5)
    tk.Button(test_window, text="Test Disallowed Goal", font=("Arial", 12), command=test_disallowed_goal).pack(pady=5)
    tk.Button(test_window, text="Test End of Period Sound", font=("Arial", 12), command=test_end_of_period_sound).pack(pady=5)
    tk.Button(test_window, text="Test Team Win Video", font=("Arial", 12), command=test_team_win_sound).pack(pady=5)
    tk.Button(test_window, text="Test Loss Sound", font=("Arial", 12), command=test_loss_sound).pack(pady=5)
    tk.Button(test_window, text="Test Live Clock", font=("Arial", 12), command=test_live_clock).pack(pady=5)

def launch_gui():
    """Main GUI window."""
    root = tk.Tk()
    root.title("NHL Score Tracker")
    root.geometry("400x250")

    tk.Label(root, text="NHL Score Tracker", font=("Arial", 16)).pack(pady=20)

    start_button = tk.Button(root, text="Start Live Feed", font=("Arial", 12), command=track_scores)
    start_button.pack(pady=10)

    # Button to open the test function selection window
    test_button = tk.Button(root, text="Test Functions", font=("Arial", 12), command=open_test_window)
    test_button.pack(pady=10)

    tk.Button(root, text="EXIT", font=("Arial", 12), command=exit_button).pack(pady=5)

    root.mainloop()

#Main execution
if __name__ == "__main__":
    launch_gui()