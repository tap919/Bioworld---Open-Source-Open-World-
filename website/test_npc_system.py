"""
Tests for the NPC and Crafting System
=====================================
Tests cover:
- NPC creation and interaction
- Mathematically fair reward distribution
- Bartering system
- Base elements and crafting
- Shelters and camps
- Disease research progress
- Loot tables
"""

import os
import tempfile
import pytest
from app import app, init_db, calculate_fair_reward, select_weighted_reward, _calculate_unique_build_bonus


@pytest.fixture
def client():
    """Create test client with fresh database."""
    # Create a temporary file for the database
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Health check should return healthy status."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'version' in data


class TestNPCSystem:
    """Tests for NPC creation and interaction."""
    
    def test_create_npc(self, client):
        """Should create NPC with valid data."""
        npc_data = {
            'name': 'Test Helper',
            'npc_type': 'helper',
            'role': 'aid',
            'location_zone': 'test_zone',
            'rarity': 'rare'
        }
        response = client.post('/api/npcs', json=npc_data)
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
        assert data['name'] == 'Test Helper'
        assert data['rarity'] == 'rare'
    
    def test_create_npc_invalid_type(self, client):
        """Should reject NPC with invalid type."""
        npc_data = {
            'name': 'Invalid NPC',
            'npc_type': 'invalid_type',
            'role': 'aid'
        }
        response = client.post('/api/npcs', json=npc_data)
        assert response.status_code == 400
        assert 'Invalid npc_type' in response.get_json()['error']
    
    def test_create_npc_invalid_role(self, client):
        """Should reject NPC with invalid role."""
        npc_data = {
            'name': 'Invalid NPC',
            'npc_type': 'helper',
            'role': 'invalid_role'
        }
        response = client.post('/api/npcs', json=npc_data)
        assert response.status_code == 400
        assert 'Invalid role' in response.get_json()['error']
    
    def test_npc_interaction(self, client):
        """Should interact with NPC and receive reward."""
        # Create NPC first
        npc_data = {
            'name': 'Reward Giver',
            'npc_type': 'helper',
            'role': 'coins',
            'rarity': 'common'
        }
        create_response = client.post('/api/npcs', json=npc_data)
        npc_id = create_response.get_json()['id']
        
        # Interact with NPC
        interaction_data = {
            'player_id': 'player-001',
            'player_level': 5,
            'player_luck': 1.0
        }
        response = client.post(f'/api/npcs/{npc_id}/interact', json=interaction_data)
        assert response.status_code == 200
        data = response.get_json()
        assert 'reward' in data
        assert data['reward']['type'] == 'coins'
        assert data['reward']['amount'] > 0
    
    def test_npc_interaction_not_found(self, client):
        """Should return 404 for non-existent NPC."""
        response = client.post('/api/npcs/non-existent/interact', json={'player_id': 'test'})
        assert response.status_code == 404
    
    def test_get_npcs(self, client):
        """Should list all NPCs."""
        # Create some NPCs
        for i in range(3):
            client.post('/api/npcs', json={
                'name': f'NPC {i}',
                'npc_type': 'helper',
                'role': 'aid'
            })
        
        response = client.get('/api/npcs')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['npcs']) == 3
    
    def test_get_npcs_filtered(self, client):
        """Should filter NPCs by type and role."""
        client.post('/api/npcs', json={'name': 'Helper', 'npc_type': 'helper', 'role': 'aid'})
        client.post('/api/npcs', json={'name': 'Merchant', 'npc_type': 'merchant', 'role': 'trade'})
        
        response = client.get('/api/npcs?type=helper')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['npcs']) == 1
        assert data['npcs'][0]['npc_type'] == 'helper'


class TestFairRewardCalculation:
    """Tests for mathematically fair reward system."""
    
    def test_fair_reward_scales_with_level(self):
        """Higher levels should get higher rewards."""
        # Run multiple times to verify trend since there's variance
        low_sum = sum(calculate_fair_reward(1, 'common', 'coins') for _ in range(100))
        high_sum = sum(calculate_fair_reward(10, 'common', 'coins') for _ in range(100))
        assert high_sum > low_sum
    
    def test_fair_reward_scales_with_rarity(self):
        """Rarer NPCs should give better rewards."""
        common = sum(calculate_fair_reward(5, 'common', 'coins') for _ in range(100))
        legendary = sum(calculate_fair_reward(5, 'legendary', 'coins') for _ in range(100))
        assert legendary > common
    
    def test_fair_reward_bounded_variance(self):
        """Rewards should stay within reasonable bounds."""
        for _ in range(100):
            reward = calculate_fair_reward(5, 'common', 'coins')
            # Base value for common coins at level 5 should be around 10 * 1.0 * 1.0 * (1 + log(6)*0.5)
            # With ±20% variance, should be bounded
            assert reward > 0
            assert reward < 100  # Reasonable upper bound for common rewards


class TestWeightedRewardSelection:
    """Tests for weighted random loot selection."""
    
    def test_weighted_selection_respects_weights(self):
        """Higher weight items should be selected more often."""
        entries = [
            {'item': 'common', 'weight': 90, 'rarity': 'common', 'min_amount': 1, 'max_amount': 1},
            {'item': 'rare', 'weight': 10, 'rarity': 'rare', 'min_amount': 1, 'max_amount': 1}
        ]
        
        results = {'common': 0, 'rare': 0}
        for _ in range(1000):
            result = select_weighted_reward(entries)
            results[result['item']] += 1
        
        # Common should be selected approximately 90% of the time
        assert results['common'] > results['rare'] * 5  # At least 5x more common
    
    def test_weighted_selection_luck_affects_rare(self):
        """Player luck should increase rare item selection."""
        entries = [
            {'item': 'common', 'weight': 50, 'rarity': 'common', 'min_amount': 1, 'max_amount': 1},
            {'item': 'rare', 'weight': 50, 'rarity': 'rare', 'min_amount': 1, 'max_amount': 1}
        ]
        
        # Normal luck
        normal_rare = sum(1 for _ in range(1000) if select_weighted_reward(entries, 1.0)['item'] == 'rare')
        
        # High luck
        high_rare = sum(1 for _ in range(1000) if select_weighted_reward(entries, 2.0)['item'] == 'rare')
        
        # High luck should get more rare items
        assert high_rare > normal_rare
    
    def test_weighted_selection_empty_entries(self):
        """Should handle empty entries gracefully."""
        result = select_weighted_reward([])
        assert result is None


class TestBarteringSystem:
    """Tests for bartering functionality."""
    
    def test_create_barter(self, client):
        """Should create barter transaction."""
        barter_data = {
            'initiator_id': 'player-001',
            'recipient_id': 'player-002',
            'offered_items': [{'item_id': 'elem-001', 'quantity': 5}],
            'requested_items': [{'item_id': 'tool-001', 'quantity': 1}]
        }
        response = client.post('/api/barter/create', json=barter_data)
        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'pending'
        assert 'id' in data
    
    def test_accept_barter(self, client):
        """Should accept pending barter."""
        # Create barter
        barter_data = {
            'initiator_id': 'player-001',
            'recipient_id': 'player-002',
            'offered_items': [{'item_id': 'elem-001', 'quantity': 5}],
            'requested_items': [{'item_id': 'tool-001', 'quantity': 1}]
        }
        create_response = client.post('/api/barter/create', json=barter_data)
        barter_id = create_response.get_json()['id']
        
        # Accept barter
        response = client.post(f'/api/barter/{barter_id}/accept')
        assert response.status_code == 200
        assert response.get_json()['status'] == 'completed'
    
    def test_decline_barter(self, client):
        """Should decline pending barter."""
        # Create barter
        barter_data = {
            'initiator_id': 'player-001',
            'recipient_id': 'player-002',
            'offered_items': [{'item_id': 'elem-001', 'quantity': 5}],
            'requested_items': [{'item_id': 'tool-001', 'quantity': 1}]
        }
        create_response = client.post('/api/barter/create', json=barter_data)
        barter_id = create_response.get_json()['id']
        
        # Decline barter
        response = client.post(f'/api/barter/{barter_id}/decline')
        assert response.status_code == 200
        assert response.get_json()['status'] == 'declined'
    
    def test_get_barters(self, client):
        """Should get barter transactions for player."""
        # Create barter
        barter_data = {
            'initiator_id': 'player-001',
            'recipient_id': 'player-002',
            'offered_items': [{'item_id': 'elem-001', 'quantity': 5}],
            'requested_items': [{'item_id': 'tool-001', 'quantity': 1}]
        }
        client.post('/api/barter/create', json=barter_data)
        
        response = client.get('/api/barter?player_id=player-001')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['barters']) == 1


class TestBaseElements:
    """Tests for base elements system."""
    
    def test_create_element(self, client):
        """Should create base element."""
        element_data = {
            'name': 'Test Element',
            'element_type': 'organic',
            'rarity': 'common',
            'description': 'A test element',
            'research_contribution': 0.5
        }
        response = client.post('/api/elements', json=element_data)
        assert response.status_code == 201
        assert 'id' in response.get_json()
    
    def test_create_element_invalid_type(self, client):
        """Should reject element with invalid type."""
        element_data = {
            'name': 'Invalid Element',
            'element_type': 'invalid_type'
        }
        response = client.post('/api/elements', json=element_data)
        assert response.status_code == 400
    
    def test_get_elements(self, client):
        """Should list all elements."""
        client.post('/api/elements', json={'name': 'Carbon', 'element_type': 'organic'})
        client.post('/api/elements', json={'name': 'Silicon', 'element_type': 'inorganic'})
        
        response = client.get('/api/elements')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['elements']) == 2


class TestToolsSystem:
    """Tests for tools system."""
    
    def test_create_tool(self, client):
        """Should create tool."""
        tool_data = {
            'name': 'Test Tool',
            'tool_type': 'crafting',
            'tier': 2,
            'durability': 150
        }
        response = client.post('/api/tools', json=tool_data)
        assert response.status_code == 201
        assert 'id' in response.get_json()
    
    def test_create_tool_invalid_type(self, client):
        """Should reject tool with invalid type."""
        tool_data = {
            'name': 'Invalid Tool',
            'tool_type': 'invalid_type'
        }
        response = client.post('/api/tools', json=tool_data)
        assert response.status_code == 400
    
    def test_get_tools(self, client):
        """Should list all tools."""
        client.post('/api/tools', json={'name': 'Hammer', 'tool_type': 'construction'})
        client.post('/api/tools', json={'name': 'Scanner', 'tool_type': 'research'})
        
        response = client.get('/api/tools')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['tools']) == 2


class TestCraftableItems:
    """Tests for craftable items system."""
    
    def test_create_craftable(self, client):
        """Should create craftable item."""
        craftable_data = {
            'name': 'Test Jetpack',
            'item_type': 'jetpack',
            'category': 'transport',
            'craft_time_seconds': 600,
            'research_bonus': 0.15
        }
        response = client.post('/api/craftables', json=craftable_data)
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
        assert data['category'] == 'transport'
    
    def test_create_craftable_invalid_category(self, client):
        """Should reject craftable with invalid category."""
        craftable_data = {
            'name': 'Invalid Item',
            'item_type': 'jetpack',
            'category': 'invalid_category'
        }
        response = client.post('/api/craftables', json=craftable_data)
        assert response.status_code == 400
    
    def test_craft_item(self, client):
        """Should craft an item."""
        # Create craftable first
        craftable_data = {
            'name': 'Craftable Item',
            'item_type': 'jetpack',
            'category': 'transport'
        }
        create_response = client.post('/api/craftables', json=craftable_data)
        craftable_id = create_response.get_json()['id']
        
        # Craft the item
        craft_data = {
            'player_id': 'player-001',
            'craftable_id': craftable_id
        }
        response = client.post('/api/craft', json=craft_data)
        assert response.status_code == 201
        data = response.get_json()
        assert 'player_item_id' in data
    
    def test_get_craftables_by_category(self, client):
        """Should filter craftables by category."""
        client.post('/api/craftables', json={'name': 'Jetpack', 'item_type': 'jetpack', 'category': 'transport'})
        client.post('/api/craftables', json={'name': 'Tent', 'item_type': 'shelter', 'category': 'shelter'})
        
        response = client.get('/api/craftables?category=transport')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['craftables']) == 1
        assert data['craftables'][0]['category'] == 'transport'


class TestShelters:
    """Tests for shelters system."""
    
    def test_create_shelter(self, client):
        """Should create shelter."""
        shelter_data = {
            'player_id': 'player-001',
            'name': 'Test Shelter',
            'shelter_type': 'research_station',
            'location': {'x': 100.0, 'y': 200.0, 'z': 50.0}
        }
        response = client.post('/api/shelters', json=shelter_data)
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
        assert data['research_bonus'] == 0.3  # research_station bonus
    
    def test_create_shelter_invalid_type(self, client):
        """Should reject shelter with invalid type."""
        shelter_data = {
            'player_id': 'player-001',
            'name': 'Invalid Shelter',
            'shelter_type': 'invalid_type'
        }
        response = client.post('/api/shelters', json=shelter_data)
        assert response.status_code == 400
    
    def test_get_shelters_by_player(self, client):
        """Should get shelters for specific player."""
        client.post('/api/shelters', json={
            'player_id': 'player-001', 'name': 'Shelter 1', 'shelter_type': 'tent'
        })
        client.post('/api/shelters', json={
            'player_id': 'player-002', 'name': 'Shelter 2', 'shelter_type': 'cabin'
        })
        
        response = client.get('/api/shelters?player_id=player-001')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['shelters']) == 1


class TestResearchProgress:
    """Tests for disease research progress system."""
    
    def test_add_research_contribution(self, client):
        """Should add research contribution."""
        research_data = {
            'disease_id': 'disease-001',
            'player_id': 'player-001',
            'contribution_amount': 10.0
        }
        response = client.post('/api/research-progress', json=research_data)
        assert response.status_code == 201
        data = response.get_json()
        assert data['base_contribution'] == 10.0
    
    def test_unique_build_bonus(self, client):
        """Should calculate unique build bonus for element combinations."""
        research_data = {
            'disease_id': 'disease-001',
            'player_id': 'player-001',
            'contribution_amount': 10.0,
            'elements_used': ['organic', 'catalyst', 'biological']
        }
        response = client.post('/api/research-progress', json=research_data)
        assert response.status_code == 201
        data = response.get_json()
        assert data['unique_build_bonus'] > 0
        assert data['total_contribution'] > data['base_contribution']
    
    def test_unique_build_bonus_calculation(self):
        """Test the unique build bonus calculation directly."""
        # Single element
        single = _calculate_unique_build_bonus(['organic'])
        assert single > 0
        
        # Synergy combination
        synergy = _calculate_unique_build_bonus(['organic', 'catalyst'])
        assert synergy > single
        
        # Triple synergy
        triple = _calculate_unique_build_bonus(['organic', 'biological', 'catalyst'])
        assert triple > synergy
    
    def test_get_research_progress(self, client):
        """Should get research progress with totals."""
        # Add contributions
        for i in range(3):
            client.post('/api/research-progress', json={
                'disease_id': 'disease-001',
                'player_id': 'player-001',
                'contribution_amount': 10.0
            })
        
        response = client.get('/api/research-progress?disease_id=disease-001')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['progress']) == 3
        assert data['total_contribution'] >= 30.0


class TestLootTables:
    """Tests for loot table system."""
    
    def test_create_loot_table(self, client):
        """Should create loot table."""
        loot_data = {
            'name': 'Test Loot',
            'entries': [
                {'item': 'coins', 'weight': 50, 'min_amount': 1, 'max_amount': 10},
                {'item': 'rare_item', 'weight': 10, 'min_amount': 1, 'max_amount': 1}
            ]
        }
        response = client.post('/api/loot-tables', json=loot_data)
        assert response.status_code == 201
        data = response.get_json()
        assert data['total_weight'] == 60
        assert data['entry_count'] == 2
    
    def test_roll_loot_table(self, client):
        """Should roll on loot table and get result."""
        # Create loot table
        loot_data = {
            'name': 'Roll Test',
            'entries': [
                {'item': 'test_item', 'weight': 100, 'rarity': 'common', 'min_amount': 1, 'max_amount': 5}
            ]
        }
        create_response = client.post('/api/loot-tables', json=loot_data)
        table_id = create_response.get_json()['id']
        
        # Roll on table
        response = client.post(f'/api/loot-tables/{table_id}/roll', json={'player_luck': 1.0})
        assert response.status_code == 200
        data = response.get_json()
        assert data['result']['item'] == 'test_item'
        assert 1 <= data['result']['amount'] <= 5
    
    def test_roll_loot_table_not_found(self, client):
        """Should return 404 for non-existent loot table."""
        response = client.post('/api/loot-tables/non-existent/roll', json={})
        assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
