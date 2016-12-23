from unittest import TestCase

from decimal import Decimal
from supplychainpy import model_inventory
from supplychainpy._helpers._pickle_config import deserialise_config

from supplychainpy.bi._recommendation_state_machine import SkuMachine
from supplychainpy.bi._recommendations import SKUStates
from supplychainpy.sample_data.config import ABS_FILE_PATH


class TestRecommendations(TestCase):
    def setUp(self):
        self.STATES = ('EXCESS_RANK', 'SHORTAGE_RANK', 'TRAFFIC_LIGHT', 'CLASSIFICATION', 'FORECAST', 'RECOMMENDATION',
                       'INVENTORY_TURNS', 'START')

        self.orders_analysis = model_inventory.analyse(file_path=ABS_FILE_PATH['COMPLETE_CSV_SM'],
                                                       z_value=Decimal(1.28),
                                                       reorder_cost=Decimal(5000),
                                                       file_type="csv",
                                                       length=12)

        self.forecast = deserialise_config(ABS_FILE_PATH['FORECAST_PICKLE'])

        self.recommend = SkuMachine()
        self.states = SKUStates(analysed_orders=self.orders_analysis, forecast=self.forecast)
        self.recommend.add_state("start", self.states.initialise_machine)
        self.recommend.add_state("excess_rank", self.states.excess_rank)
        self.recommend.add_state("shortage_rank", self.states.shortage_rank)
        self.recommend.add_state("inventory_turns", self.states.inventory_turns)
        self.recommend.add_state("classification", self.states.classification)
        self.recommend.add_state("traffic_light", self.states.traffic_light)
        self.recommend.add_state("forecast", self.states.forecast)
        self.recommend.add_state("recommendation", self.recommend, end_state=1)
        self.recommend.set_start("start")

    def test_add_states(self):
        self.assertEqual(8, len(self.recommend.handlers))

    def test_add_states_key(self):
        for state in self.recommend.handlers.keys():
            self.assertIn(state, self.STATES)

    def test_recommendations(self):
        completed_recommendations =[]
        for sku in self.orders_analysis:
            completed_recommendations.append(self.recommend.run(sku.sku_id))
        self.assertEqual(len(completed_recommendations), len(self.orders_analysis))

    def test_recommendations_coverage(self):
        completed_recommendations =[]
        sku_ids = [i.sku_id for i in self.orders_analysis]
        for sku in self.orders_analysis:
            completed_recommendations.append(self.recommend.run(sku.sku_id)[1])
        for i in completed_recommendations:
            self.assertIn(i, sku_ids)

