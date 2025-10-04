import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Guess High Low")

# Color definitions
BACKGROUND_COLOR = (50, 120, 80)   # Green background
CARD_FRONT_COLOR = (255, 255, 255) # White card front
CARD_BACK_COLOR = (30, 60, 120)    # Blue card back
BUTTON_COLOR = (200, 200, 200)     # Button color
TEXT_COLOR = (0, 0, 0)             # Text color
BORDER_COLOR = (0, 0, 0)           # Border color

# Card class
class Card:
    def __init__(self, card_id, name, value, suit=None):
        self.card_id = card_id
        self.name = name
        self.value = value
        self.suit = suit
        self.is_revealed = False
        
    def __str__(self):
        if self.suit:
            return f"{self.suit}{self.name}"
        else:
            return self.name

# Game class
class PokerGame:
    def __init__(self):
        self.deck = []
        self.card_deck = []
        self.card_dealed = []
        self.card_revealed = []
        self.previous_deck_order = []  # Save pre-shuffle order
        
        self.player_score = 0
        self.computer_card = None
        self.player_card = None
        self.game_state = "idle"  # idle, dealing, waiting_guess, revealing, game_over
        self.deal_start_time = 0
        self.result_start_time = 0
        
        self.show_hint_dialog = False
        self.hint_probabilities = {}
        self.show_result = False
        self.result_info = {}
        self.show_shuffle_dialog = False
        self.shuffle_info = {}
        self.show_instruction_dialog = False  # New instruction dialog flag
        
        self.fonts = {
            "small": pygame.font.Font(None, 24),
            "medium": pygame.font.Font(None, 32),
            "large": pygame.font.Font(None, 48)
        }
        
        self.buttons = self.create_buttons()
        self.initialize_deck()
        
    def create_buttons(self):
        """Create all buttons"""
        button_size = (150, 50)
        buttons = {}
        
        # Main control buttons
        buttons["start_new"] = pygame.Rect(SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT - 80, *button_size)
        buttons["exit"] = pygame.Rect(SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT - 80, *button_size)
        
        # Game action buttons
        buttons["instruction"] = pygame.Rect(50, 250, *button_size)  # New instruction button
        buttons["hint"] = pygame.Rect(50, 350, *button_size)
        buttons["shuffle"] = pygame.Rect(50, 450, *button_size)
        
        # Guess buttons
        buttons["higher"] = pygame.Rect(SCREEN_WIDTH - 200, 250, *button_size)
        buttons["tie"] = pygame.Rect(SCREEN_WIDTH - 200, 350, *button_size)
        buttons["lower"] = pygame.Rect(SCREEN_WIDTH - 200, 450, *button_size)
        
        # Dialog OK buttons - separate positions for different dialogs
        buttons["hint_ok"] = pygame.Rect(SCREEN_WIDTH//2 - 75, 450, *button_size)
        buttons["shuffle_ok"] = pygame.Rect(SCREEN_WIDTH//2 - 75, 500, *button_size)
        buttons["instruction_ok"] = pygame.Rect(SCREEN_WIDTH//2 - 75, 550, *button_size)  # New instruction OK button
        
        return buttons
    
    def initialize_deck(self):
        """Initialize 54 cards"""
        self.deck = []
        self.card_deck = []
        self.card_dealed = []
        self.card_revealed = []
        self.previous_deck_order = []
        
        # Card values mapping
        values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
            '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
        }
        
        suits = ["Spade", "Heart", "Diamond", "Club"]
        suit_signs = ["♠", "♥", "♦", "♣"]
        
        # Create standard cards
        for suit, sign in zip(suits, suit_signs):
            for name, value in values.items():
                card_id = f"{suit}_{name}"
                card = Card(card_id, name, value, sign)
                self.deck.append(card)
        
        # Create jokers
        little_joker = Card("little_joker", "Little Joker", 15)
        big_joker = Card("big_joker", "Big Joker", 16)
        
        self.deck.extend([little_joker, big_joker])
        self.card_deck = self.deck.copy()
        self.previous_deck_order = self.card_deck.copy()
        
    def shuffle_deck(self):
        """Shuffle deck and save pre-shuffle order"""
        if self.card_deck:
            self.previous_deck_order = self.card_deck.copy()
            random.shuffle(self.card_deck)
            
            # Prepare shuffle dialog info
            self.shuffle_info = {
                "previous_order": self.previous_deck_order[:10],  # Show first 10 cards
                "current_order": self.card_deck[:10],            # Show first 10 cards
                "total_cards": len(self.card_deck)
            }
            self.show_shuffle_dialog = True
        
    def deal_cards(self, count):
        """Deal specified number of cards"""
        if len(self.card_deck) < count:
            return None
            
        dealt_cards = []
        for _ in range(count):
            card = self.card_deck.pop(0)
            self.card_dealed.append(card)
            dealt_cards.append(card)
            
        return dealt_cards
    
    def reveal_card(self, card):
        """Reveal specified card"""
        if card in self.card_dealed:
            card.is_revealed = True
            self.card_dealed.remove(card)
            self.card_revealed.append(card)
    
    def start_new_game(self):
        """Start new game"""
        self.initialize_deck()
        self.shuffle_deck()
        self.player_score = 0
        self.computer_card = None
        self.player_card = None
        self.game_state = "idle"
        self.next_round()
        
    def next_round(self):
        """Go to next round"""
        if len(self.card_deck) >= 2:
            # Deal two cards
            dealt_cards = self.deal_cards(2)
            if dealt_cards:
                self.computer_card = dealt_cards[0]
                self.player_card = dealt_cards[1]
                
                # Reset card states
                self.computer_card.is_revealed = False
                self.player_card.is_revealed = False
                
                self.game_state = "dealing"
                self.deal_start_time = pygame.time.get_ticks()
                print(f"Dealt cards: Computer={self.computer_card}, Player={self.player_card}")  # Debug
        else:
            self.game_state = "game_over"
    
    def calculate_probabilities(self):
        """Calculate probabilities for different guesses"""
        if not self.computer_card or not self.player_card:
            return {"higher": 0, "lower": 0, "tie": 0, "remaining": 0}
            
        computer_value = self.computer_card.value
        total_cards = len(self.card_deck) + 1  # +1 for player's unrevealed card
        higher_count = 0
        lower_count = 0
        tie_count = 0
        
        # Calculate probabilities from remaining deck and player's card
        all_unrevealed = self.card_deck + [self.player_card]
        
        for card in all_unrevealed:
            if card.value > computer_value:
                higher_count += 1
            elif card.value < computer_value:
                lower_count += 1
            else:
                tie_count += 1
        
        return {
            "higher": higher_count / total_cards if total_cards > 0 else 0,
            "lower": lower_count / total_cards if total_cards > 0 else 0,
            "tie": tie_count / total_cards if total_cards > 0 else 0,
            "remaining": total_cards
        }
    
    def check_guess(self, player_guess):
        """Check player's guess and calculate score"""
        if not self.computer_card or not self.player_card:
            return False, 0, False
            
        # Reveal player card
        self.reveal_card(self.player_card)
        
        computer_value = self.computer_card.value
        player_value = self.player_card.value
        
        # Determine if guess is correct
        is_correct = False
        if player_guess == "higher" and player_value > computer_value:
            is_correct = True
        elif player_guess == "lower" and player_value < computer_value:
            is_correct = True
        elif player_guess == "tie" and player_value == computer_value:
            is_correct = True
        
        # Calculate score
        score_added = 0
        bonus = False
        
        if is_correct:
            # Calculate probability of this guess
            probabilities = self.calculate_probabilities()
            guess_probability = probabilities.get(player_guess, 0)
            
            if guess_probability < 0.1:  # Less than 10% probability
                score_added = 100
                bonus = True
            else:
                score_added = 10
                bonus = False
                
            self.player_score += score_added
        
        return is_correct, score_added, bonus
    
    def draw_card(self, card, position):
        """Draw a card"""
        card_size = (120, 180)
        card_rect = pygame.Rect(position, card_size)
        
        if card.is_revealed:
            # Draw card front
            pygame.draw.rect(screen, CARD_FRONT_COLOR, card_rect)
            pygame.draw.rect(screen, BORDER_COLOR, card_rect, 2)
            
            # Draw card info
            if card.suit:
                suit_text = self.fonts["medium"].render(card.suit, True, TEXT_COLOR)
                name_text = self.fonts["medium"].render(card.name, True, TEXT_COLOR)
            else:
                name_text = self.fonts["small"].render(card.name, True, TEXT_COLOR)
                
            suit_pos = (position[0] + 10, position[1] + 10)
            name_pos = (position[0] + card_size[0]//2 - name_text.get_width()//2, 
                       position[1] + card_size[1]//2 - name_text.get_height()//2)
            
            if card.suit:
                screen.blit(suit_text, suit_pos)
            screen.blit(name_text, name_pos)
        else:
            # Draw card back
            pygame.draw.rect(screen, CARD_BACK_COLOR, card_rect)
            pygame.draw.rect(screen, BORDER_COLOR, card_rect, 2)
    
    def draw_button(self, button_name, text):
        """Draw a single button"""
        if button_name in self.buttons:
            button_rect = self.buttons[button_name]
            pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
            pygame.draw.rect(screen, BORDER_COLOR, button_rect, 2)
            
            text_surface = self.fonts["small"].render(text, True, TEXT_COLOR)
            text_pos = (button_rect.centerx - text_surface.get_width()//2,
                       button_rect.centery - text_surface.get_height()//2)
            screen.blit(text_surface, text_pos)
    
    def draw_buttons(self):
        """Draw buttons based on game state"""
        # Always show main control buttons
        self.draw_button("start_new", "New Game")
        self.draw_button("exit", "Exit")
        
        if self.game_state == "waiting_guess":
            # Show game action buttons
            self.draw_button("instruction", "Instruction")  # New instruction button
            self.draw_button("hint", "Hint")
            self.draw_button("shuffle", "Shuffle")
            
            # Show guess buttons
            self.draw_button("higher", "Mine Higher")
            self.draw_button("tie", "Tie")
            self.draw_button("lower", "Mine Lower")
            
        elif self.game_state == "game_over":
            self.draw_button("start_new", "Play Again")
    
    def draw_instruction_dialog(self):
        """Draw instruction dialog"""
        # Draw dialog background
        dialog_rect = pygame.Rect(50, 50, 500, 600)
        pygame.draw.rect(screen, (240, 240, 240), dialog_rect)
        pygame.draw.rect(screen, BORDER_COLOR, dialog_rect, 3)
        
        # Draw title
        title = self.fonts["medium"].render("Game Instructions", True, TEXT_COLOR)
        screen.blit(title, (dialog_rect.centerx - title.get_width()//2, dialog_rect.y + 20))
        
        # Instruction text lines
        instructions = [
            "HOW TO PLAY:",
            "",
            "1. Click 'Hint' to view probabilities",
            "2. Guess if your card is:",
            "   - HIGHER than computer's card",
            "   - LOWER than computer's card", 
            "   - TIE (same value)",
            "3. Click 'Shuffle' to shuffle the remaining deck",
            "",
            "SCORING:",
            "- Correct guess: +10 points",
            "- Correct guess with <10% probability: +100 BONUS!",
            "- Wrong guess: 0 points"
        ]
        
        # Draw instruction text
        y_offset = 60
        for line in instructions:
            text_surface = self.fonts["small"].render(line, True, TEXT_COLOR)
            screen.blit(text_surface, (dialog_rect.x + 20, dialog_rect.y + y_offset))
            y_offset += 25
        
        # Draw OK button at the bottom
        self.draw_button("instruction_ok", "OK")
    
    def draw_hint_dialog(self):
        """Draw hint dialog"""
        # Draw dialog background
        dialog_rect = pygame.Rect(50, 100, 500, 480)
        pygame.draw.rect(screen, (240, 240, 240), dialog_rect)
        pygame.draw.rect(screen, BORDER_COLOR, dialog_rect, 3)
        
        # Draw title
        title = self.fonts["medium"].render("Hint - Probabilities", True, TEXT_COLOR)
        screen.blit(title, (dialog_rect.x + 20, dialog_rect.y + 20))
        
        # Draw probabilities
        y_offset = 70
        for guess_type in ["higher", "lower", "tie"]:
            prob = self.hint_probabilities.get(guess_type, 0)
            prob_text = f"{guess_type.capitalize()}: {prob:.1%}"
            text_surface = self.fonts["small"].render(prob_text, True, TEXT_COLOR)
            screen.blit(text_surface, (dialog_rect.x + 30, dialog_rect.y + y_offset))
            y_offset += 30
        
        # Draw remaining cards
        remaining = self.hint_probabilities.get("remaining", 0)
        rem_text = f"Remaining cards: {remaining}"
        text_surface = self.fonts["small"].render(rem_text, True, TEXT_COLOR)
        screen.blit(text_surface, (dialog_rect.x + 30, dialog_rect.y + y_offset + 20))
        
        # Draw OK button
        self.draw_button("hint_ok", "OK")
    
    def draw_shuffle_dialog(self):
        """Draw shuffle dialog"""
        # Draw dialog background
        dialog_rect = pygame.Rect(50, 100, 500, 500)  # Increased height
        pygame.draw.rect(screen, (240, 240, 240), dialog_rect)
        pygame.draw.rect(screen, BORDER_COLOR, dialog_rect, 3)
        
        # Draw title
        title = self.fonts["medium"].render("Deck Shuffled", True, TEXT_COLOR)
        screen.blit(title, (dialog_rect.centerx - title.get_width()//2, dialog_rect.y + 20))
        
        # Show total cards
        total_text = f"Cards shuffled. Remaining cards: {self.shuffle_info['total_cards']}"
        total_surface = self.fonts["small"].render(total_text, True, TEXT_COLOR)
        screen.blit(total_surface, (dialog_rect.x + 20, dialog_rect.y + 60))
        
        # Show first 10 cards changes
        y_offset = 100
        
        # Before shuffle title
        before_title = self.fonts["small"].render("Before Shuffle (First 10 cards):", True, (100, 100, 100))
        screen.blit(before_title, (dialog_rect.x + 20, dialog_rect.y + y_offset))
        y_offset += 30
        
        # Pre-shuffle order
        prev_cards_text = ""
        for i, card in enumerate(self.shuffle_info["previous_order"]):
            if i > 0:
                prev_cards_text += ", "
            prev_cards_text += card.card_id     # card.card_id instead of str(card)
        
        # Split long text for display
        prev_lines = self.split_text(prev_cards_text, 45)
        for line in prev_lines:
            prev_surface = self.fonts["small"].render(line, True, TEXT_COLOR)
            screen.blit(prev_surface, (dialog_rect.x + 30, dialog_rect.y + y_offset))
            y_offset += 25
        
        y_offset += 10
        
        # After shuffle title
        after_title = self.fonts["small"].render("After Shuffle (First 10 cards):", True, (100, 100, 100))
        screen.blit(after_title, (dialog_rect.x + 20, dialog_rect.y + y_offset))
        y_offset += 30
        
        # Post-shuffle order
        current_cards_text = ""
        for i, card in enumerate(self.shuffle_info["current_order"]):
            if i > 0:
                current_cards_text += ", "
            current_cards_text += card.card_id      # card.card_id instead of str(card)
        
        # Split long text for display
        current_lines = self.split_text(current_cards_text, 45)
        for line in current_lines:
            current_surface = self.fonts["small"].render(line, True, TEXT_COLOR)
            screen.blit(current_surface, (dialog_rect.x + 30, dialog_rect.y + y_offset))
            y_offset += 25
        
        # Draw OK button at the bottom
        self.draw_button("shuffle_ok", "OK")
    
    def split_text(self, text, max_length):
        """Split long text into multiple lines"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) <= max_length:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def draw_result_message(self):
        """Draw result message"""
        is_correct = self.result_info.get("is_correct", False)
        score_added = self.result_info.get("score_added", 0)
        bonus = self.result_info.get("bonus", False)
        
        # Draw message background
        msg_rect = pygame.Rect(50, 250, 400, 100)
        pygame.draw.rect(screen, (240, 240, 240), msg_rect)
        pygame.draw.rect(screen, BORDER_COLOR, msg_rect, 3)
        
        # Draw result text
        if is_correct:
            if bonus:
                result_text = "BONUS! +100 Points!"
                color = (0, 200, 0)  # Green
            else:
                result_text = f"Correct! +{score_added} Points"
                color = (0, 150, 0)  # Dark green
        else:
            result_text = "Missed. +0 Points"
            color = (200, 0, 0)  # Red
            
        text_surface = self.fonts["medium"].render(result_text, True, color)
        screen.blit(text_surface, 
                   (msg_rect.centerx - text_surface.get_width()//2,
                    msg_rect.centery - text_surface.get_height()//2))
    
    def draw_game_over(self):
        """Draw game over screen"""
        # Draw congratulations message
        congrats_text = self.fonts["large"].render("Congratulations!", True, (255, 215, 0))
        score_text = self.fonts["medium"].render(f"Final Score: {self.player_score}", True, TEXT_COLOR)
        
        screen.blit(congrats_text, 
                   (SCREEN_WIDTH//2 - congrats_text.get_width()//2, 300))
        screen.blit(score_text,
                   (SCREEN_WIDTH//2 - score_text.get_width()//2, 380))
        
        # Draw simple "confetti" (colored circles)
        for i in range(20):
            color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), 
                                 (255, 255, 0), (255, 0, 255), (0, 255, 255)])
            pos = (random.randint(100, SCREEN_WIDTH-100), random.randint(100, 500))
            pygame.draw.circle(screen, color, pos, 5)
    
    def draw(self):
        """Draw game screen"""
        screen.fill(BACKGROUND_COLOR)
        
        # Draw cards
        if self.computer_card:
            self.draw_card(self.computer_card, (SCREEN_WIDTH//2 - 60, 100))
        if self.player_card:
            self.draw_card(self.player_card, (SCREEN_WIDTH//2 - 60, 400))
        
        # Draw buttons
        self.draw_buttons()
        
        # Draw score
        score_text = self.fonts["medium"].render(f"Score: {self.player_score}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 20))
        
        # Draw instruction dialog
        if self.show_instruction_dialog:
            self.draw_instruction_dialog()
            
        # Draw hint dialog
        if self.show_hint_dialog:
            self.draw_hint_dialog()
            
        # Draw shuffle dialog
        if self.show_shuffle_dialog:
            self.draw_shuffle_dialog()
            
        # Draw result message
        if self.show_result:
            self.draw_result_message()
            
        # Draw game over screen
        if self.game_state == "game_over":
            self.draw_game_over()
        
        pygame.display.flip()
    
    def handle_click(self, mouse_pos):
        """Handle mouse click"""
        for button_name, button_rect in self.buttons.items():
            if button_rect.collidepoint(mouse_pos):
                return self.handle_button_click(button_name)
        return "continue"
    
    def handle_button_click(self, button_name):
        """Handle button click"""
        print(f"Button clicked: {button_name}")  # Debug
        
        if button_name == "start_new":
            if self.game_state in ["idle", "game_over"]:
                self.start_new_game()
                self.show_result = False
                self.show_hint_dialog = False
                self.show_shuffle_dialog = False
                self.show_instruction_dialog = False
            
        elif button_name == "exit":
            return "exit"
            
        elif button_name == "instruction" and self.game_state == "waiting_guess":
            self.show_instruction_dialog = True
            
        elif button_name == "shuffle" and self.game_state == "waiting_guess":
            self.shuffle_deck()
            
        elif button_name == "hint" and self.game_state == "waiting_guess":
            self.hint_probabilities = self.calculate_probabilities()
            self.show_hint_dialog = True
            
        elif button_name == "instruction_ok" and self.show_instruction_dialog:
            self.show_instruction_dialog = False
            
        elif button_name == "hint_ok" and self.show_hint_dialog:
            self.show_hint_dialog = False
            
        elif button_name == "shuffle_ok" and self.show_shuffle_dialog:
            self.show_shuffle_dialog = False
            print("Shuffle dialog closed")  # Debug
            
        elif button_name in ["higher", "lower", "tie"] and self.game_state == "waiting_guess":
            is_correct, score_added, bonus = self.check_guess(button_name)
            self.show_result = True
            self.result_info = {
                "is_correct": is_correct,
                "score_added": score_added,
                "bonus": bonus
            }
            self.game_state = "revealing"
            self.result_start_time = pygame.time.get_ticks()
        
        return "continue"
    
    def update(self):
        """Update game state"""
        # Handle automatic computer card reveal
        if (self.game_state == "dealing" and 
            self.computer_card and 
            not self.computer_card.is_revealed):
            # Wait 1 second then reveal computer card
            if pygame.time.get_ticks() - self.deal_start_time > 1000:
                self.reveal_card(self.computer_card)
                self.game_state = "waiting_guess"
        
        # Handle automatic next round after showing result for 2 seconds
        if (self.game_state == "revealing" and 
            self.show_result and
            pygame.time.get_ticks() - self.result_start_time > 2000):
            
            if len(self.card_deck) >= 2:
                self.next_round()
                self.show_result = False
            else:
                self.game_state = "game_over"
                self.show_result = False

# Main game loop
def main():
    clock = pygame.time.Clock()
    game = PokerGame()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    result = game.handle_click(mouse_pos)
                    if result == "exit":
                        running = False
        
        game.update()
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()