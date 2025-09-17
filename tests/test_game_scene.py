"""
Unit tests for the GameScene class.
Tests scene initialization, system integration, and game loop functionality.
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
import pygame
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scenes.game_scene import GameScene


class TestGameScene(unittest.TestCase):
    """Test cases for GameScene class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock pygame to avoid initialization issues
        pygame.init = Mock()
        pygame.display.set_mode = Mock(return_value=Mock())
        pygame.display.set_caption = Mock()
        pygame.time.Clock = Mock()
        pygame.font.Font = Mock(return_value=Mock())
        
        # Create mock game instance
        self.mock_game = Mock()
        self.mock_game.get_screen_size.return_value = (800, 600)
        self.mock_game.config = {
            'game': {
                'player_speed': 100,
                'player_start_x': 400,
                'player_start_y': 300,
                'max_inventory_size': 20,
                'default_map': 'assets/maps/test_map.json'
            }
        }
        
        # Create game scene
        self.game_scene = GameScene()
    
    def tearDown(self):
        """Clean up after each test method."""
        if hasattr(self, 'game_scene'):
            self.game_scene.cleanup()
    
    @patch('scenes.game_scene.InputSystem')
    @patch('scenes.game_scene.MapSystem')
    @patch('scenes.game_scene.MapRenderer')
    @patch('scenes.game_scene.Camera')
    @patch('scenes.game_scene.CollisionSystem')
    @patch('scenes.game_scene.CombatSystem')
    @patch('scenes.game_scene.ItemSystem')
    @patch('scenes.game_scene.UISystem')
    @patch('scenes.game_scene.Player')
    @patch('scenes.game_scene.Inventory')
    @patch('scenes.game_scene.HealthBar')
    @patch('scenes.game_scene.ExperienceBar')
    @patch('scenes.game_scene.InventoryUI')
    def test_initialization(self, mock_inventory_ui, mock_exp_bar, mock_health_bar,
                          mock_inventory, mock_player, mock_ui_system, mock_item_system,
                          mock_combat_system, mock_collision_system, mock_camera,
                          mock_map_renderer, mock_map_system, mock_input_system):
        """Test GameScene initialization."""
        # Mock the map loading to avoid file system dependencies
        mock_map_system_instance = Mock()
        mock_map_system.return_value = mock_map_system_instance
        mock_map_system_instance.load_map.side_effect = Exception("Map not found")
        
        # Initialize the scene
        self.game_scene.initialize(self.mock_game)
        
        # Verify initialization
        self.assertTrue(self.game_scene.initialized)
        self.assertEqual(self.game_scene.name, "GameScene")
        
        # Verify systems were created
        mock_input_system.assert_called_once()
        mock_map_system.assert_called_once()
        mock_map_renderer.assert_called_once()
        mock_camera.assert_called_once_with(800, 600)
        mock_collision_system.assert_called_once()
        mock_combat_system.assert_called_once()
        mock_item_system.assert_called_once()
        mock_ui_system.assert_called_once()
        
        # Verify player was created
        mock_player.assert_called_once_with(400, 300)
        mock_inventory.assert_called_once_with(20)
        
        # Verify UI elements were created
        mock_health_bar.assert_called_once()
        mock_exp_bar.assert_called_once()
        mock_inventory_ui.assert_called_once()
    
    def test_scene_properties(self):
        """Test basic scene properties."""
        self.assertEqual(self.game_scene.get_name(), "GameScene")
        self.assertFalse(self.game_scene.is_initialized())
        self.assertFalse(self.game_scene.is_active())
    
    @patch('scenes.game_scene.InputSystem')
    @patch('scenes.game_scene.MapSystem')
    @patch('scenes.game_scene.Player')
    def test_handle_event_inventory_toggle(self, mock_player, mock_map_system, mock_input_system):
        """Test inventory toggle event handling."""
        # Mock the map loading
        mock_map_system_instance = Mock()
        mock_map_system.return_value = mock_map_system_instance
        mock_map_system_instance.load_map.side_effect = Exception("Map not found")
        
        # Initialize scene
        with patch.multiple('scenes.game_scene',
                          MapRenderer=Mock(), Camera=Mock(), CollisionSystem=Mock(),
                          CombatSystem=Mock(), ItemSystem=Mock(), UISystem=Mock(),
                          Inventory=Mock(), HealthBar=Mock(), ExperienceBar=Mock(),
                          InventoryUI=Mock()):
            self.game_scene.initialize(self.mock_game)
        
        # Create mock event
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_i
        
        # Test inventory toggle
        self.assertFalse(self.game_scene.inventory_open)
        result = self.game_scene.handle_event(mock_event)
        self.assertTrue(result)
        self.assertTrue(self.game_scene.inventory_open)
    
    @patch('scenes.game_scene.InputSystem')
    @patch('scenes.game_scene.MapSystem')
    @patch('scenes.game_scene.Player')
    def test_handle_event_pause_toggle(self, mock_player, mock_map_system, mock_input_system):
        """Test pause toggle event handling."""
        # Mock the map loading
        mock_map_system_instance = Mock()
        mock_map_system.return_value = mock_map_system_instance
        mock_map_system_instance.load_map.side_effect = Exception("Map not found")
        
        # Initialize scene
        with patch.multiple('scenes.game_scene',
                          MapRenderer=Mock(), Camera=Mock(), CollisionSystem=Mock(),
                          CombatSystem=Mock(), ItemSystem=Mock(), UISystem=Mock(),
                          Inventory=Mock(), HealthBar=Mock(), ExperienceBar=Mock(),
                          InventoryUI=Mock()):
            self.game_scene.initialize(self.mock_game)
        
        # Create mock event
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_p
        
        # Test pause toggle
        self.assertFalse(self.game_scene.paused)
        result = self.game_scene.handle_event(mock_event)
        self.assertTrue(result)
        self.assertTrue(self.game_scene.paused)
    
    def test_update_when_paused(self):
        """Test that update does nothing when paused."""
        self.game_scene.paused = True
        
        # Mock systems
        self.game_scene.input_system = Mock()
        self.game_scene.player = Mock()
        
        # Update should do nothing when paused
        self.game_scene.update(0.016)
        
        # Verify systems were not updated
        self.game_scene.input_system.update.assert_not_called()
        self.game_scene.player.update.assert_not_called()
    
    @patch('scenes.game_scene.InputSystem')
    @patch('scenes.game_scene.MapSystem')
    @patch('scenes.game_scene.Player')
    def test_update_normal(self, mock_player, mock_map_system, mock_input_system):
        """Test normal update cycle."""
        # Mock the map loading
        mock_map_system_instance = Mock()
        mock_map_system.return_value = mock_map_system_instance
        mock_map_system_instance.load_map.side_effect = Exception("Map not found")
        
        # Initialize scene with mocked systems
        with patch.multiple('scenes.game_scene',
                          MapRenderer=Mock(), Camera=Mock(), CollisionSystem=Mock(),
                          CombatSystem=Mock(), ItemSystem=Mock(), UISystem=Mock(),
                          Inventory=Mock(), HealthBar=Mock(), ExperienceBar=Mock(),
                          InventoryUI=Mock(), MapTransitionSystem=Mock()):
            self.game_scene.initialize(self.mock_game)
        
        # Update scene
        self.game_scene.update(0.016)
        
        # Verify systems were updated
        self.game_scene.input_system.update.assert_called_once()
        self.game_scene.player.handle_input.assert_called_once_with(self.game_scene.input_system)
        self.game_scene.player.update.assert_called_once_with(0.016)
        self.game_scene.camera.update.assert_called_once_with(0.016)
        self.game_scene.ui_system.update.assert_called_once_with(0.016)
    
    def test_render(self):
        """Test scene rendering."""
        # Mock screen
        mock_screen = Mock()
        
        # Mock systems and objects
        self.game_scene.map_renderer = Mock()
        self.game_scene.camera = Mock()
        self.game_scene.current_map_data = {'test': 'data'}
        self.game_scene.player = Mock()
        self.game_scene.ui_system = Mock()
        self.game_scene.enemies = [Mock(), Mock()]
        self.game_scene.items = [Mock()]
        
        # Render scene
        self.game_scene.render(mock_screen)
        
        # Verify rendering calls
        self.game_scene.map_renderer.render.assert_called_once_with(mock_screen, self.game_scene.camera)
        self.game_scene.player.render.assert_called_once_with(mock_screen, self.game_scene.camera)
        self.game_scene.ui_system.render.assert_called_once_with(mock_screen)
        
        # Verify enemies and items were rendered
        for enemy in self.game_scene.enemies:
            enemy.render.assert_called_once_with(mock_screen, self.game_scene.camera)
        
        for item in self.game_scene.items:
            item.render.assert_called_once_with(mock_screen, self.game_scene.camera)
    
    def test_render_paused(self):
        """Test rendering when paused."""
        # Mock screen and font
        mock_screen = Mock()
        mock_screen.get_size.return_value = (800, 600)
        mock_screen.get_width.return_value = 800
        mock_screen.get_height.return_value = 600
        
        # Mock pygame.Surface for overlay
        with patch('pygame.Surface') as mock_surface:
            mock_overlay = Mock()
            mock_surface.return_value = mock_overlay
            
            # Mock font rendering
            with patch('pygame.font.Font') as mock_font_class:
                mock_font = Mock()
                mock_font_class.return_value = mock_font
                
                mock_text = Mock()
                mock_text.get_rect.return_value = Mock()
                mock_font.render.return_value = mock_text
                
                # Set paused state
                self.game_scene.paused = True
                
                # Mock other rendering components
                self.game_scene.map_renderer = Mock()
                self.game_scene.camera = Mock()
                self.game_scene.current_map_data = {'test': 'data'}
                self.game_scene.player = Mock()
                self.game_scene.ui_system = Mock()
                self.game_scene.enemies = []
                self.game_scene.items = []
                
                # Render scene
                self.game_scene.render(mock_screen)
                
                # Verify pause overlay was created and rendered
                mock_surface.assert_called_with(mock_screen.get_size())
                mock_overlay.set_alpha.assert_called_with(128)
                mock_overlay.fill.assert_called_with((0, 0, 0))
                mock_screen.blit.assert_called()
    
    def test_object_management(self):
        """Test adding and removing enemies and items."""
        from objects.enemy import Enemy
        from objects.item import Item
        
        # Create mock objects
        mock_enemy = Mock(spec=Enemy)
        mock_item = Mock(spec=Item)
        
        # Test adding objects
        self.game_scene.add_enemy(mock_enemy)
        self.game_scene.add_item(mock_item)
        
        self.assertIn(mock_enemy, self.game_scene.enemies)
        self.assertIn(mock_item, self.game_scene.items)
        
        # Test removing objects
        self.game_scene.remove_enemy(mock_enemy)
        self.game_scene.remove_item(mock_item)
        
        self.assertNotIn(mock_enemy, self.game_scene.enemies)
        self.assertNotIn(mock_item, self.game_scene.items)
    
    def test_scene_lifecycle(self):
        """Test scene lifecycle methods."""
        # Test on_enter
        self.game_scene.on_enter()
        self.assertTrue(self.game_scene.is_active())
        
        # Test on_exit
        self.game_scene.on_exit()
        self.assertFalse(self.game_scene.is_active())
        
        # Test on_pause and on_resume
        self.game_scene.on_pause()
        self.game_scene.on_resume()
        # These methods just print messages, so we just verify they don't crash
    
    def test_cleanup(self):
        """Test scene cleanup."""
        # Add some mock objects
        self.game_scene.enemies = [Mock(), Mock()]
        self.game_scene.items = [Mock()]
        self.game_scene.ui_system = Mock()
        self.game_scene.map_system = Mock()
        
        # Cleanup
        self.game_scene.cleanup()
        
        # Verify cleanup
        self.assertEqual(len(self.game_scene.enemies), 0)
        self.assertEqual(len(self.game_scene.items), 0)
        self.game_scene.ui_system.clear_elements.assert_called_once()
        self.game_scene.map_system.clear_cache.assert_called_once()
    
    def test_default_map_creation(self):
        """Test default map creation when loading fails."""
        default_map = self.game_scene._create_default_map()
        
        self.assertIsInstance(default_map, dict)
        self.assertIn('width', default_map)
        self.assertIn('height', default_map)
        self.assertIn('tile_size', default_map)
        self.assertIn('layers', default_map)
        
        layers = default_map['layers']
        self.assertIn('background', layers)
        self.assertIn('collision', layers)
        self.assertIn('objects', layers)


if __name__ == '__main__':
    unittest.main()