import pymunk
import pygame
import random
import math
import imageio
import os
import sys

# --- Configuration ---
WIDTH, HEIGHT = 600, 600
FPS = 50
STEPS_PER_FRAME = 5  # Physics steps per render frame for stability
TOTAL_WHITE_BALLS = 69
TOTAL_RED_BALLS = 26
BALL_RADIUS = 12
BALL_MASS = 1
GRAVITY = 900.0
PADDLE_SPEED = 8.0  # Radians per second
MIX_TIME = 3.0      # Seconds to mix before drawing
DRAW_INTERVAL = 0.5 # Seconds between draws
OUTPUT_GIF = "powerball_simulation.gif"
AIR_DRAG = 0.995    # Air resistance factor (1.0 = no drag)

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLACK = (20, 20, 20)
GRAY = (100, 100, 100)
GOLD = (255, 215, 0)
GREEN = (0, 200, 0)

class PowerballSim:
    def __init__(self):
        pygame.init()
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        self.frames = []
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 32, bold=True)
        
    def setup_physics(self, ball_count, is_red_draw=False):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, GRAVITY)
        self.balls = []
        self.drawn_balls = []
        self.is_red_draw = is_red_draw
        self.pending_draw = False # Flag to open the chute
        
        # --- Create Chamber (Circle with Exit Chute) ---
        center = (WIDTH // 2, HEIGHT // 2)
        radius = 250
        num_segments = 60
        
        # Create static walls but leave a gap at the bottom
        gap_width = BALL_RADIUS * 4.0 # Wider gap
        gap_angle_width = math.asin((gap_width / 2) / radius) * 2
        
        start_angle = math.pi / 2 + gap_angle_width / 2
        end_angle = math.pi / 2 - gap_angle_width / 2 + 2 * math.pi
        
        # Draw the main circular wall
        for i in range(num_segments):
            t = i / num_segments
            angle = start_angle + t * (end_angle - start_angle)
            next_angle = start_angle + (i + 1) / num_segments * (end_angle - start_angle)
            
            p1 = (center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle))
            p2 = (center[0] + radius * math.cos(next_angle), center[1] + radius * math.sin(next_angle))
            
            wall = pymunk.Segment(self.space.static_body, p1, p2, 5)
            wall.elasticity = 0.6
            wall.friction = 0.5
            self.space.add(wall)

        # Create the Exit Chute (Funnel)
        # Add funnel walls to guide balls in
        funnel_h = 60
        funnel_w = 100
        
        chute_y_start = center[1] + radius * math.sin(start_angle)
        chute_x_left = center[0] + radius * math.cos(start_angle)
        chute_x_right = center[0] + radius * math.cos(end_angle)
        
        # Left funnel wall (sloped)
        l1 = (chute_x_left - 20, chute_y_start - 20)
        l2 = (chute_x_left, chute_y_start + funnel_h)
        left_wall = pymunk.Segment(self.space.static_body, l1, l2, 5)
        left_wall.elasticity = 0.2
        left_wall.friction = 0.1
        self.space.add(left_wall)
        
        # Right funnel wall (sloped)
        r1 = (chute_x_right + 20, chute_y_start - 20)
        r2 = (chute_x_right, chute_y_start + funnel_h)
        right_wall = pymunk.Segment(self.space.static_body, r1, r2, 5)
        right_wall.elasticity = 0.2
        right_wall.friction = 0.1
        self.space.add(right_wall)
        
        # Sensor at the bottom of the chute
        sensor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        sensor_body.position = (center[0], chute_y_start + funnel_h - 10)
        sensor_shape = pymunk.Segment(sensor_body, (-gap_width/2, 0), (gap_width/2, 0), 5)
        sensor_shape.sensor = True
        
        self.space.add(sensor_body, sensor_shape)
        self.sensor_shape = sensor_shape # Keep ref

        # --- Create Paddle (Agitator with Deflectors) ---
        self.paddle_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.paddle_body.position = center
        self.paddle_body.angular_velocity = PADDLE_SPEED
        
        # Cross shape paddle with deflectors
        paddle_len = 180
        thickness = 8
        
        # Main arms
        s1 = pymunk.Segment(self.paddle_body, (-paddle_len, 0), (paddle_len, 0), thickness)
        s2 = pymunk.Segment(self.paddle_body, (0, -paddle_len), (0, paddle_len), thickness)
        
        # Deflectors (Angled tips to scoop balls)
        deflector_len = 40
        angle_offset = math.radians(45)
        
        def add_deflector(x, y, angle_base):
            dx = deflector_len * math.cos(angle_base + angle_offset)
            dy = deflector_len * math.sin(angle_base + angle_offset)
            return pymunk.Segment(self.paddle_body, (x, y), (x + dx, y + dy), thickness)

        d1 = add_deflector(paddle_len, 0, 0)
        d2 = add_deflector(-paddle_len, 0, math.pi)
        d3 = add_deflector(0, paddle_len, math.pi/2)
        d4 = add_deflector(0, -paddle_len, -math.pi/2)
        
        # Add body and all shapes to space
        self.space.add(self.paddle_body)
        for s in [s1, s2, d1, d2, d3, d4]:
            s.elasticity = 0.8
            s.friction = 0.8
            self.space.add(s)
        
        # --- Create Balls (with Imperfections) ---
        # Grid layout for initialization to prevent overlap
        cols = 8
        start_x = center[0] - 100
        start_y = center[1] - 100
        
        numbers = list(range(1, ball_count + 1))
        random.shuffle(numbers) # Randomize initial positions
        
        for i, number in enumerate(numbers):
            row = i // cols
            col = i % cols
            pos = (start_x + col * (BALL_RADIUS * 2 + 2), start_y + row * (BALL_RADIUS * 2 + 2))
            
            # Manufacturing Imperfections (Chaos Theory)
            # Vary mass and radius by +/- 2%
            radius_var = random.gauss(BALL_RADIUS, BALL_RADIUS * 0.02)
            mass_var = random.gauss(BALL_MASS, BALL_MASS * 0.02)
            
            moment = pymunk.moment_for_circle(mass_var, 0, radius_var)
            body = pymunk.Body(mass_var, moment)
            body.position = pos
            
            shape = pymunk.Circle(body, radius_var)
            shape.elasticity = 0.9
            shape.friction = 0.4
            shape.collision_type = 0 # Ball type
            
            self.space.add(body, shape)
            self.balls.append({"body": body, "shape": shape, "number": number, "active": True})

    def check_sensor(self):
        if not self.pending_draw: return None
        
        # Query the space for shapes overlapping the sensor
        # shape_query returns a list of ShapeQueryInfo objects
        query_info = self.space.shape_query(self.sensor_shape)
        
        for info in query_info:
            shape = info.shape
            # Find which ball this shape belongs to
            for ball in self.balls:
                if ball["shape"] == shape and ball["active"]:
                    ball["active"] = False
                    self.space.remove(ball["body"], ball["shape"])
                    self.drawn_balls.append(ball["number"])
                    self.pending_draw = False
                    print(f"  -> Ball {ball['number']} detected in chute!")
                    return ball["number"]
        return None

    def apply_air_drag(self):
        for ball in self.balls:
            if ball["active"]:
                # Apply simple linear drag
                ball["body"].velocity = ball["body"].velocity * AIR_DRAG

    def draw(self, message=""):
        self.surface.fill(BLACK)
        
        # Draw Chamber
        pygame.draw.circle(self.surface, GRAY, (WIDTH // 2, HEIGHT // 2), 255, 5)
        
        # Draw Paddle
        p_pos = self.paddle_body.position
        angle = self.paddle_body.angle
        # We need to calculate endpoints based on rotation
        paddle_len = 180
        
        # Arm 1
        p1_x = p_pos.x + paddle_len * math.cos(angle)
        p1_y = p_pos.y + paddle_len * math.sin(angle)
        p2_x = p_pos.x - paddle_len * math.cos(angle)
        p2_y = p_pos.y - paddle_len * math.sin(angle)
        pygame.draw.line(self.surface, GOLD, (p1_x, p1_y), (p2_x, p2_y), 8)
        
        # Arm 2
        p3_x = p_pos.x + paddle_len * math.cos(angle + math.pi/2)
        p3_y = p_pos.y + paddle_len * math.sin(angle + math.pi/2)
        p4_x = p_pos.x - paddle_len * math.cos(angle + math.pi/2)
        p4_y = p_pos.y - paddle_len * math.sin(angle + math.pi/2)
        pygame.draw.line(self.surface, GOLD, (p3_x, p3_y), (p4_x, p4_y), 8)

        # Draw Balls
        for ball in self.balls:
            if not ball["active"]: continue
            
            pos = ball["body"].position
            color = RED if self.is_red_draw else WHITE
            
            pygame.draw.circle(self.surface, color, (int(pos.x), int(pos.y)), BALL_RADIUS)
            
            # Draw Number
            text = self.font.render(str(ball["number"]), True, BLACK)
            text_rect = text.get_rect(center=(int(pos.x), int(pos.y)))
            self.surface.blit(text, text_rect)

        # Draw UI
        if message:
            msg_surf = self.large_font.render(message, True, GREEN)
            self.surface.blit(msg_surf, (20, 20))
            
        # Draw "Drawn Balls" list
        y_offset = 60
        title = self.font.render("Drawn Numbers:", True, WHITE)
        self.surface.blit(title, (20, y_offset))
        
        for i, num in enumerate(self.drawn_balls):
            num_text = self.large_font.render(str(num), True, GOLD)
            self.surface.blit(num_text, (20 + i * 50, y_offset + 30))

        # Capture frame
        # Convert Pygame surface to numpy array for imageio
        # Only save every 3rd frame to save memory
        if len(self.frames) % 1 == 0: # Logic handled by caller or here? 
            # Actually, we can just skip appending.
            # But we need a counter. Let's use a static var or just random chance?
            # Better: use a frame counter in the class.
            pass
            
        view = pygame.surfarray.array3d(self.surface)
        view = view.transpose([1, 0, 2]) # Pygame is (w, h, c), imageio needs (h, w, c)
        
        # Simple skip logic: only keep if total frames < 500 or skip
        if len(self.frames) < 600:
             self.frames.append(view)

    def select_ball(self):
        # Enable the sensor to accept a ball
        self.pending_draw = True
        
        # Wait for physics to push a ball into the chute
        # We'll give it a max time to avoid infinite loops if balls get stuck
        max_wait_frames = FPS * 2 # 2 seconds max wait (reduced from 5)
        
        for _ in range(max_wait_frames):
            # Check sensor manually every frame
            caught_ball = self.check_sensor()
            if caught_ball:
                return caught_ball
                
            for _ in range(STEPS_PER_FRAME):
                self.apply_air_drag()
                self.space.step(1.0 / (FPS * STEPS_PER_FRAME))
            self.draw("Waiting for ball to drop...")
            
        # If timeout, force pick (fallback)
        print("  ! Timeout waiting for ball drop. Forcing selection.")
        self.pending_draw = False
        # Fallback logic: pick closest to chute
        candidates = [b for b in self.balls if b["active"]]
        if candidates:
            # Sort by Y position (lowest first)
            candidates.sort(key=lambda b: b["body"].position.y, reverse=True)
            selected = candidates[0]
            selected["active"] = False
            self.space.remove(selected["body"], selected["shape"])
            self.drawn_balls.append(selected["number"]) # Fix: Append to list
            return selected["number"]
        return None

    def run_simulation(self):
        print("Starting Powerball Simulation...")
        
        # --- PHASE 1: White Balls ---
        print("Simulating White Balls...")
        self.setup_physics(TOTAL_WHITE_BALLS, is_red_draw=False)
        
        # Mixing Phase
        for _ in range(int(MIX_TIME * FPS)):
            for _ in range(STEPS_PER_FRAME):
                self.apply_air_drag()
                self.space.step(1.0 / (FPS * STEPS_PER_FRAME))
            self.draw("Mixing White Balls...")
            
        # Drawing Phase (5 balls)
        for i in range(5):
            # Mix a bit between draws
            for _ in range(int(DRAW_INTERVAL * FPS)):
                for _ in range(STEPS_PER_FRAME):
                    self.apply_air_drag()
                    self.space.step(1.0 / (FPS * STEPS_PER_FRAME))
                self.draw(f"Drawing Ball {i+1}...")
            
            number = self.select_ball()
            if number:
                # self.drawn_balls.append(number) # Already appended in callback
                print(f"White Ball {i+1}: {number}")
                
        white_balls_result = list(self.drawn_balls)
        
        # Transition Phase
        for _ in range(int(1.0 * FPS)):
            self.draw("Switching to Red Ball...")

        # --- PHASE 2: Red Ball ---
        print("Simulating Red Ball...")
        # Keep the white balls in the display list but reset physics for red
        saved_white_balls = list(self.drawn_balls)
        self.setup_physics(TOTAL_RED_BALLS, is_red_draw=True)
        self.drawn_balls = saved_white_balls # Restore list for UI
        
        # Mixing Phase
        for _ in range(int(MIX_TIME * FPS)):
            for _ in range(STEPS_PER_FRAME):
                self.apply_air_drag()
                self.space.step(1.0 / (FPS * STEPS_PER_FRAME))
            self.draw("Mixing Red Ball...")
            
        # Drawing Phase (1 ball)
        for _ in range(int(DRAW_INTERVAL * FPS)):
            for _ in range(STEPS_PER_FRAME):
                self.apply_air_drag()
                self.space.step(1.0 / (FPS * STEPS_PER_FRAME))
            self.draw("Drawing Powerball...")
            
        number = self.select_ball()
        if number:
            # self.drawn_balls.append(number) # Already appended in callback
            print(f"Red Ball: {number}")

        # Final Freeze
        for _ in range(int(2.0 * FPS)):
            self.draw("Simulation Complete!")

        # Save GIF
        print(f"Saving simulation to {OUTPUT_GIF}...")
        imageio.mimsave(OUTPUT_GIF, self.frames, fps=FPS)
        print("Done!")
        
        return self.drawn_balls

if __name__ == "__main__":
    sim = PowerballSim()
    results = sim.run_simulation()
    print("\n" + "="*30)
    print("FINAL PREDICTION")
    print("="*30)
    print(f"White Balls: {results[:5]}")
    print(f"Powerball:   {results[5]}")
    print("="*30)
