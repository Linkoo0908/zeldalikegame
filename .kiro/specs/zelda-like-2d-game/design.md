# Design Document

## Overview

젤다의 전설과 비슷한 2D 탑뷰 게임을 파이썬과 Pygame을 사용하여 개발합니다. 게임은 객체지향 설계 원칙을 따르며, 모듈화된 구조로 구성됩니다. 게임 엔진의 핵심 시스템들(렌더링, 입력 처리, 충돌 감지, 상태 관리)을 분리하여 유지보수성과 확장성을 확보합니다.

## Architecture

### Technology Stack
- **Python 3.8+**: 메인 프로그래밍 언어
- **Pygame 2.0+**: 게임 개발 프레임워크
- **JSON**: 맵 데이터 및 게임 설정 저장
- **PIL/Pillow**: 이미지 처리 (필요시)

### High-Level Architecture

```
Game Application
├── Core Engine
│   ├── Game Loop
│   ├── Scene Manager
│   └── Resource Manager
├── Game Systems
│   ├── Input System
│   ├── Rendering System
│   ├── Physics/Collision System
│   └── Audio System
├── Game Objects
│   ├── Player
│   ├── Enemies
│   ├── Items
│   └── Environment
└── Game States
    ├── Menu State
    ├── Game State
    └── Inventory State
```

## Components and Interfaces

### 1. Core Engine Components

#### Game Class
메인 게임 루프와 전체 시스템을 관리하는 핵심 클래스입니다.

```python
class Game:
    def __init__(self)
    def run(self)
    def update(self, dt)
    def render(self)
    def handle_events(self)
```

#### Scene Manager
게임의 다양한 상태(메뉴, 게임플레이, 인벤토리)를 관리합니다.

```python
class SceneManager:
    def push_scene(self, scene)
    def pop_scene(self)
    def change_scene(self, scene)
    def update(self, dt)
    def render(self, screen)
```

#### Resource Manager
게임 리소스(이미지, 사운드, 맵 데이터)의 로딩과 캐싱을 담당합니다.

```python
class ResourceManager:
    def load_image(self, path)
    def load_sound(self, path)
    def load_map(self, path)
    def get_resource(self, key)
```

### 2. Game Systems

#### Input System
키보드 입력을 처리하고 게임 액션으로 변환합니다.

```python
class InputSystem:
    def update(self)
    def is_key_pressed(self, key)
    def is_key_just_pressed(self, key)
    def get_movement_vector(self)
```

#### Rendering System
모든 게임 객체의 렌더링을 담당합니다.

```python
class RenderSystem:
    def render_sprite(self, sprite, position)
    def render_ui(self, ui_elements)
    def render_map(self, map_data, camera)
```

#### Collision System
게임 객체 간의 충돌 감지와 처리를 담당합니다.

```python
class CollisionSystem:
    def check_collision(self, obj1, obj2)
    def check_map_collision(self, obj, map_data)
    def resolve_collision(self, obj1, obj2)
```

### 3. Game Objects

#### GameObject Base Class
모든 게임 객체의 기본 클래스입니다.

```python
class GameObject:
    def __init__(self, x, y)
    def update(self, dt)
    def render(self, screen, camera)
    def get_bounds(self)
```

#### Player Class
플레이어 캐릭터를 나타내는 클래스입니다.

```python
class Player(GameObject):
    def __init__(self, x, y)
    def handle_input(self, input_system)
    def attack(self)
    def take_damage(self, damage)
    def collect_item(self, item)
```

#### Enemy Class
적 캐릭터의 기본 클래스입니다.

```python
class Enemy(GameObject):
    def __init__(self, x, y, enemy_type)
    def ai_update(self, player_pos)
    def attack_player(self, player)
    def take_damage(self, damage)
```

#### Item Class
수집 가능한 아이템을 나타내는 클래스입니다.

```python
class Item(GameObject):
    def __init__(self, x, y, item_type)
    def on_collect(self, player)
    def get_effect(self)
```

## Data Models

### Player Data
```python
player_data = {
    "position": {"x": 0, "y": 0},
    "health": {"current": 100, "max": 100},
    "experience": {"current": 0, "level": 1},
    "inventory": [],
    "stats": {
        "attack": 10,
        "defense": 5,
        "speed": 100
    }
}
```

### Map Data
```python
map_data = {
    "width": 20,
    "height": 15,
    "tile_size": 32,
    "layers": {
        "background": [[tile_id, ...], ...],
        "collision": [[0, 1, 0, ...], ...],
        "objects": [
            {"type": "enemy", "x": 100, "y": 200, "enemy_type": "goblin"},
            {"type": "item", "x": 150, "y": 250, "item_type": "health_potion"}
        ]
    }
}
```

### Item Data
```python
item_data = {
    "health_potion": {
        "name": "Health Potion",
        "type": "consumable",
        "effect": {"health": 50},
        "sprite": "health_potion.png"
    },
    "sword": {
        "name": "Iron Sword",
        "type": "weapon",
        "effect": {"attack": 15},
        "sprite": "iron_sword.png"
    }
}
```

## Error Handling

### Exception Hierarchy
```python
class GameError(Exception):
    """Base exception for game-related errors"""
    pass

class ResourceLoadError(GameError):
    """Raised when resource loading fails"""
    pass

class MapLoadError(GameError):
    """Raised when map loading fails"""
    pass

class SaveLoadError(GameError):
    """Raised when save/load operations fail"""
    pass
```

### Error Handling Strategy
1. **Resource Loading**: 리소스 로딩 실패 시 기본 리소스로 대체
2. **Map Loading**: 맵 로딩 실패 시 기본 맵으로 대체
3. **Save/Load**: 저장/로드 실패 시 사용자에게 알림 후 계속 진행
4. **Runtime Errors**: 게임 크래시 방지를 위한 try-catch 블록 사용

## Testing Strategy

### Unit Testing
- **GameObject Classes**: 각 게임 객체의 기본 동작 테스트
- **Game Systems**: 입력, 충돌, 렌더링 시스템의 개별 테스트
- **Data Models**: 데이터 구조의 유효성 검증

### Integration Testing
- **Player-Enemy Interaction**: 전투 시스템 통합 테스트
- **Item Collection**: 아이템 수집 및 인벤토리 시스템 테스트
- **Map Navigation**: 맵 이동 및 충돌 감지 테스트

### Manual Testing
- **Gameplay Flow**: 전체 게임 플레이 경험 테스트
- **Performance**: 프레임레이트 및 메모리 사용량 모니터링
- **User Experience**: 컨트롤 반응성 및 시각적 피드백 테스트

### Test Data
- **Mock Maps**: 다양한 크기와 복잡도의 테스트 맵
- **Test Sprites**: 기본적인 테스트용 스프라이트 이미지
- **Sample Configurations**: 다양한 게임 설정 파일

## Performance Considerations

### Optimization Strategies
1. **Sprite Batching**: 동일한 텍스처의 스프라이트들을 함께 렌더링
2. **Culling**: 화면 밖의 객체는 렌더링하지 않음
3. **Object Pooling**: 자주 생성/삭제되는 객체들의 재사용
4. **Efficient Collision Detection**: 공간 분할을 통한 충돌 감지 최적화

### Memory Management
- 사용하지 않는 리소스의 적절한 해제
- 큰 이미지 파일의 스케일링 최적화
- 게임 상태 변경 시 불필요한 객체 정리

## File Structure
```
zelda_like_game/
├── main.py                 # 게임 진입점
├── config/
│   ├── settings.json       # 게임 설정
│   └── controls.json       # 키 바인딩
├── src/
│   ├── core/
│   │   ├── game.py         # 메인 게임 클래스
│   │   ├── scene_manager.py
│   │   └── resource_manager.py
│   ├── systems/
│   │   ├── input_system.py
│   │   ├── render_system.py
│   │   └── collision_system.py
│   ├── objects/
│   │   ├── game_object.py
│   │   ├── player.py
│   │   ├── enemy.py
│   │   └── item.py
│   └── scenes/
│       ├── menu_scene.py
│       ├── game_scene.py
│       └── inventory_scene.py
├── assets/
│   ├── images/
│   ├── sounds/
│   └── maps/
└── tests/
    ├── test_player.py
    ├── test_collision.py
    └── test_game_systems.py
```