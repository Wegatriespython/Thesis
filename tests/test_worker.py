import pytest
from ..legacy.Worker import Worker
from Config import config

def test_worker_initialization():
    worker = Worker()
    assert worker.employed == False
    assert worker.employer == None
    assert worker.wage == config.INITIAL_WAGE
    assert worker.skills == config.INITIAL_SKILLS
    assert worker.offers == []
    assert worker.consumption == config.INITIAL_CONSUMPTION

def test_worker_update_state_employed():
    worker = Worker()
    worker.employed = True
    initial_skills = worker.skills
    worker.update_state()
    assert worker.skills > initial_skills

def test_worker_update_state_unemployed():
    worker = Worker()
    worker.employed = False
    initial_skills = worker.skills
    worker.update_state()
    assert worker.skills < initial_skills

def test_worker_wage_adjustment():
    worker = Worker()
    initial_wage = worker.wage
    worker.update_state()
    assert worker.wage != initial_wage
    assert worker.wage >= config.MINIMUM_WAGE

def test_worker_consume():
    worker = Worker()
    worker.employed = True
    worker.wage = 100
    class MockFirm:
        def __init__(self):
            self.inventory = 1000
    mock_firms = [MockFirm()]
    worker.consume(mock_firms)
    assert worker.consumption > 0
    assert worker.wage < 100
    assert mock_firms[0].inventory < 1000