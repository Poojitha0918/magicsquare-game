import json
import os
import app as appmod

def test_health():
    appmod.app.config['TESTING'] = True
    client = appmod.app.test_client()
    r = client.get('/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'

def test_flow_submit_valid():
    os.environ["MONGO_MOCK"] = "1"
    appmod.app.config['TESTING'] = True
    client = appmod.app.test_client()

    # list puzzles
    r = client.get('/api/puzzles')
    assert r.status_code == 200
    items = r.get_json()
    pid = items[0]['id']

    # fetch puzzle
    r = client.get(f'/api/puzzle/{pid}')
    puz = r.get_json()
    assert puz['id'] == pid

    # submit correct solution: reconstruct via siamese size
    from magic import siamese
    n = puz['size']
    sol = siamese(n)
    payload = {
        "username": "tester",
        "puzzle_id": pid,
        "solution": sol,
        "duration_ms": 12345
    }
    r = client.post('/api/submit', data=json.dumps(payload), content_type='application/json')
    j = r.get_json()
    assert j['ok'] is True

    # leaderboard
    r = client.get(f'/api/leaderboard?puzzle_id={pid}&limit=5')
    assert r.status_code == 200
    lb = r.get_json()
    assert len(lb) >= 1
