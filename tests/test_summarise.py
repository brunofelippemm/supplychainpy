import os
from decimal import Decimal
from unittest import TestCase

from supplychainpy import model_inventory
from supplychainpy.inventory.summarise import OrdersAnalysis


class TestSummariseAnalysis(TestCase):
    def setUp(self):
        app_dir = os.path.dirname(__file__, )
        rel_path = 'supplychainpy/data2.csv'
        abs_file_path = os.path.abspath(os.path.join(app_dir, '..', rel_path))

        self.__skus = ['KR202-209', 'KR202-210', 'KR202-211']

        self.__orders_analysis = model_inventory.analyse_orders_abcxyz_from_file(file_path=abs_file_path,
                                                                                 z_value=Decimal(1.28),
                                                                                 reorder_cost=Decimal(5000),
                                                                                 file_type="csv",
                                                                                 length=12)
        self.__categories = ['excess_stock', 'shortages', 'average_orders']
        self.__abc_classification = ('AX', 'AY', 'AZ', 'BX', 'BY', 'BZ', 'CX', 'CY', 'CZ')
        self.__analysis_summary = OrdersAnalysis(analysed_orders=self.__orders_analysis)
        self.__describe_sku = ['excess_cost', 'percentage_contribution_revenue', 'markup_percentage',
                               'shortage_rank', 'unit_cost', 'max_order', 'retail_price', 'classification',
                               'excess_rank', 'average_orders', 'revenue_rank', 'excess_units', 'safety_stock_units',
                               'shortage_cost', 'revenue', 'min_order', 'safety_stock_rank', 'safety_stock_cost',
                               'sku_id', 'gross_profit_margin', 'shortage_units']

        self.__abc_raw = self.__analysis_summary.abc_xyz_raw

    def test_describe_sku_length(self):
        item = [description for description in self.__analysis_summary.describe_sku('KR202-209')]
        self.assertEqual(21, len(item[0]))

    def test_describe_type_error(self):
        with self.assertRaises(expected_exception=TypeError):
            for description in self.__analysis_summary.describe_sku('KR2-0'):
                print(description)

    def test_describe_sku_keys(self):
        s = [summarised for summarised in self.__analysis_summary.describe_sku('KR202-217')]
        for key in self.__describe_sku:
            self.assertIn(key, s[0])

    # TODO-fix makes sure that all categories have are safe in this method
    def test_category_ranking_filter_top10(self):
        """Checks that the filter returns top ten shortages that are greater than the bottom ten.
            uses list of categories."""

        for category in self.__categories:
            top_ten = [item for item in
                       self.__analysis_summary.sku_ranking_filter(
                           attribute=category, count=10, reverse=True)]

            for item in top_ten:
                for bottom in [item for item in
                               self.__analysis_summary.sku_ranking_filter(
                                   attribute=category, count=10, reverse=False)]:
                    self.assertGreaterEqual(Decimal(item[category]), Decimal(bottom[category]))

    def test_category_ranking_filter_top10_attr_error(self):
        """ Tests the correct attribute name has been provided. Test uses shortage instead of shortages."""

        with self.assertRaises(expected_exception=AttributeError):
            top_ten_shortages = [item for item in
                                 self.__analysis_summary.sku_ranking_filter(
                                     attribute="shortage", count=10, reverse=True)]
            print(top_ten_shortages)

    def test_category_ranking_filter_bottom10(self):
        """Checks that the filter returns bottom ten of each category. Each value is compared against top ten for the
        same category."""
        for category in self.__categories:
            bottom_ten = [item for item in
                          self.__analysis_summary.sku_ranking_filter(
                              attribute=category, count=10, reverse=False)]

            for item in bottom_ten:
                for Top in [item for item in
                            self.__analysis_summary.sku_ranking_filter(
                                attribute=category, count=10, reverse=True)]:
                    self.assertLessEqual(Decimal(item[category]), Decimal(Top[category]))

    def test_abcxyz_summary_category_selection(self):
        # assert that every summarised cost is eqal to the cost of every sku with that
        # category in the original structure
        for category in self.__categories:
            for analysis in self.__analysis_summary.abc_xyz_summary(category=(category,)):
                self.assertEqual(1, len(analysis))

    def test_abcxyz_classification_selection(self):
        for category in self.__abc_classification:
            for summary in self.__analysis_summary.abc_xyz_summary(classification=((category,))):
                for classification in summary:
                    self.assertEqual(category, classification)

    def test_abcxyz_units_summary(self):
        pass

    def test_abcxyz_currency_summary(self):
        pass
