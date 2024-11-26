import pygame
import math
import os
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800, 480), pygame.NOFRAME)  # Setting screen size
clock = pygame.time.Clock()  # Sets up clock in project

# Define colors
WHITE = pygame.Color('antiquewhite')
RED = pygame.Color('brown1')
DARKRED = pygame.Color('brown4')
GREEN = pygame.Color('seagreen3')
DARKGREEN = pygame.Color('seagreen4')
BLUE = pygame.Color('cyan3')
DARKBLUE = pygame.Color('darkcyan')
GRAY = pygame.Color('antiquewhite3')

# Define variables
HOME, IMAGE_SELECTION, TIMER = 0, 1, 2
current_state = HOME
timer_running = False
finish = True
last_update_time = pygame.time.get_ticks()  # Record initial time
timer_seconds, time_set = 0, 60
timer_minutes = time_set
max_time_secs = time_set * 60  # Convert time_set by users to seconds

# Set the path for the USB image folder
usb_image_folder = "/media/visualtimer/ESD-USB/Image"  # USB path where images are stored

# Load image filenames from the USB "Image" folder
if os.path.exists(usb_image_folder):  # Check if the folder exists
    image_files = [f for f in os.listdir(usb_image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]  # Array to store image names
else:
    image_files = []  # If USB folder doesn't exist, no images are loaded

current_image_index = 0

# Creates a circular mask for the image
def crop_image_to_circle(image, radius):
    # Create a surface with an alpha channel (RGBA) to allow transparency
    circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

    # Create a circular mask (White circle on a transparent background)
    pygame.draw.circle(circle_surface, (255, 255, 255), (radius, radius), radius)

    # Copy the image onto the circle surface using the mask
    image_rect = image.get_rect(center=(radius, radius))
    circle_surface.blit(image, image_rect, special_flags=pygame.BLEND_RGBA_MIN)  # Use blending to apply the mask

    return circle_surface

# Display a title bar with shadow
def display_title(title, color, border):
    pygame.draw.rect(screen, GRAY, (5, 0, 797, 45), border_radius=10)  # Shadow
    pygame.draw.rect(screen, border, (-1, -10, 801, 53), border_radius=10)
    pygame.draw.rect(screen, color, (0, -10, 800, 50), border_radius=10)  # Rounded title bar
    font = pygame.font.Font(None, 40)
    text = font.render(title, True, border)
    screen.blit(text, (400 - text.get_width() // 2, 7))

# Display spokes like a clock
def draw_timer_spokes(color):
    # Filled circle with outline
    circle_border = pygame.draw.circle(screen, color, (400, 260), 200, 5)

    # Add twelve spokes (for visual decoration)
    center_x, center_y, radius = 400, 260, 195
    even_spoke_length = 30
    odd_spoke_length = 10

    for i in range(60):
        angle = math.radians(i * 6)  # 360 degrees divided by 60 = 6 degrees per spoke
        if i % 5 == 0:  # 5th spokes
            spoke_length = even_spoke_length
        else:
            spoke_length = odd_spoke_length

        start_x = center_x + radius * math.cos(angle)
        start_y = center_y + radius * math.sin(angle)
        end_x = center_x + (radius - spoke_length) * math.cos(angle)
        end_y = center_y + (radius - spoke_length) * math.sin(angle)

        # Draw the line (spoke) from the edge of the circle towards the center
        pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 3)

# Display the current image in the center of the circle (if available)
def display_image():
    if image_files:
        current_image_path = os.path.join(usb_image_folder, image_files[current_image_index])  # Get path of current image
        try:
            # Load the image
            image = pygame.image.load(current_image_path)
            # Crop the image to a circle
            circular_image = crop_image_to_circle(image, 200)
            # Draw the circular image in the center of the circle
            screen.blit(circular_image, (400 - circular_image.get_width() // 2, 260 - circular_image.get_height() // 2))
        except Exception as e:
            print(f"Error loading image {current_image_path}: {e}")

# Display a circle waning for the timer
def draw_timer_circle(screen, center, radius, time_remaining, total_time):
    full_circle = 360  # Full circle in degrees
    remaining_angle = (time_remaining / total_time) * full_circle  # Remaining angle in degrees

    # Draw the remaining portion as a "pie slice"
    points = [center]  # Start at the center of the circle
    for angle in range(0, int(remaining_angle) + 1):
        x = center[0] + radius * math.cos(math.radians(270 - angle))
        y = center[1] + radius * math.sin(math.radians(270 - angle))
        points.append((x, y))

    pygame.draw.polygon(screen, BLUE, points)

# Home screen display function
def display_home_screen():
    global image_button, timer_button

    screen.fill(WHITE)
    display_title("Home", RED, DARKRED)

    # Define button dimensions
    button_width, button_height = 200, 200
    image_button = pygame.Rect(150, 160, button_width, button_height)  # Image button
    timer_button = pygame.Rect(450, 160, button_width, button_height)  # Timer button

    # Draw image button with shadow, color, and outline
    pygame.draw.rect(screen, GRAY, image_button.move(7, 7), border_radius=15)
    pygame.draw.rect(screen, GREEN, image_button, border_radius=15)
    pygame.draw.rect(screen, DARKGREEN, image_button.inflate(6, 6), 3, border_radius=18)  # Outline

    # Draw timer button with shadow, color, and outline
    pygame.draw.rect(screen, GRAY, timer_button.move(7, 7), border_radius=15)
    pygame.draw.rect(screen, BLUE, timer_button, border_radius=15)
    pygame.draw.rect(screen, DARKBLUE, timer_button.inflate(6, 6), 3, border_radius=18)  # Outline

    # Load and position icons on buttons
    timer_UI = pygame.image.load('UI/timer.PNG')
    timer_UI = pygame.transform.smoothscale(timer_UI, (150, 150))
    screen.blit(timer_UI, (timer_button.centerx - 75, timer_button.centery - 75))  # Center the image

    camera_UI = pygame.image.load('UI/camera.PNG')
    camera_UI = pygame.transform.smoothscale(camera_UI, (150, 150))
    screen.blit(camera_UI, (image_button.centerx - 75, image_button.centery - 75))  # Center the image

    # Add text under each button
    font = pygame.font.Font(None, 24)
    text1 = font.render("Image Selection", True, DARKGREEN)
    text2 = font.render("Timer Countdown", True, DARKBLUE)
    screen.blit(text1, (image_button.centerx - text1.get_width() // 2, image_button.bottom - 20))
    screen.blit(text2, (timer_button.centerx - text2.get_width() // 2, timer_button.bottom - 20))

# Image selection screen display function
def display_image_selection_screen():
    global home_button, timer_button, current_image_index, left_rect, right_rect
    screen.fill(WHITE)
    display_title("Image Selection", GREEN, DARKGREEN)

    button_width, button_height = 50, 50
    home_button = pygame.Rect(5, 70, button_width, button_height)  # Home button
    timer_button = pygame.Rect(5, 135, button_width, button_height)  # Timer button
    side_bar = pygame.Rect(-15, 60, 80, 135)

    # Draw sidebar with shadow, color, and outline
    pygame.draw.rect(screen, GRAY, side_bar.move(5, 5), border_radius=15)
    pygame.draw.rect(screen, DARKGREEN, side_bar.inflate(5, 5), border_radius=17)
    pygame.draw.rect(screen, GREEN, side_bar, border_radius=15)

    # Draw home button with color and outline
    pygame.draw.rect(screen, RED, home_button, border_radius=15)
    pygame.draw.rect(screen, DARKRED, home_button.inflate(6, 6), 3, border_radius=18)  # Outline

    # Draw timer button with color and outline
    pygame.draw.rect(screen, BLUE, timer_button, border_radius=15)
    pygame.draw.rect(screen, DARKBLUE, timer_button.inflate(6, 6), 3, border_radius=18)  # Outline

    # Draw arrows to select images
    left_rect = pygame.Rect(600, 230, 50, 50)
    right_rect = pygame.Rect(700, 230, 50, 50)

    pygame.draw.polygon(screen, GREEN, [(left_rect.centerx, left_rect.centery), 
                                       (left_rect.centerx - 10, left_rect.centery - 20), 
                                       (left_rect.centerx - 10, left_rect.centery + 20)])
    pygame.draw.polygon(screen, GREEN, [(right_rect.centerx, right_rect.centery), 
                                       (right_rect.centerx + 10, right_rect.centery - 20), 
                                       (right_rect.centerx + 10, right_rect.centery + 20)])

    # Load and display current image
    display_image()

# Timer countdown screen display function
def display_timer_screen():
    global timer_seconds, timer_minutes
    screen.fill(WHITE)
    display_title("Timer Countdown", BLUE, DARKBLUE)

    draw_timer_spokes(RED)
    draw_timer_circle(screen, (400, 260), 195, timer_seconds, max_time_secs)

    # Timer countdown with minutes and seconds
    time_text = f"{timer_minutes:02}:{timer_seconds:02}"
    font = pygame.font.Font(None, 72)
    text = font.render(time_text, True, DARKRED)
    screen.blit(text, (400 - text.get_width() // 2, 260 - text.get_height() // 2))

# Main game loop to handle events and display appropriate screens
def main():
    global current_state, timer_seconds, timer_minutes, max_time_secs, timer_running, last_update_time, time_set, current_image_index

    while True:
        screen.fill(WHITE)
        now = pygame.time.get_ticks()  # Get the current time
        delta_time = now - last_update_time  # Calculate time difference from last update

        if current_state == HOME:
            display_home_screen()

        elif current_state == IMAGE_SELECTION:
            display_image_selection_screen()

        elif current_state == TIMER:
            display_timer_screen()

            # Handle timer countdown
            if timer_running:
                timer_seconds -= delta_time // 1000
                last_update_time = now

                if timer_seconds <= 0:
                    timer_seconds = 0
                    timer_minutes -= 1

                    if timer_minutes <= 0:
                        timer_running = False
                        finish = True
                        # Add a beep or other action when time finishes (optional)
                        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                if current_state == HOME:
                    if image_button.collidepoint(mouse_x, mouse_y):
                        current_state = IMAGE_SELECTION  # Go to Image Selection screen
                    elif timer_button.collidepoint(mouse_x, mouse_y):
                        current_state = TIMER  # Go to Timer Countdown screen

                elif current_state == IMAGE_SELECTION:
                    if home_button.collidepoint(mouse_x, mouse_y):
                        current_state = HOME  # Go back to Home screen
                    elif timer_button.collidepoint(mouse_x, mouse_y):
                        current_state = TIMER  # Go to Timer Countdown screen
                    elif left_rect.collidepoint(mouse_x, mouse_y):
                        current_image_index = (current_image_index - 1) % len(image_files)  # Go to previous image
                    elif right_rect.collidepoint(mouse_x, mouse_y):
                        current_image_index = (current_image_index + 1) % len(image_files)  # Go to next image

                elif current_state == TIMER:
                    if mouse_x < 200:  # Stop the timer
                        timer_running = False

        clock.tick(30)  # 30 FPS limit to control updates

if __name__ == '__main__':
    main()
