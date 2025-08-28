# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """Test case to read a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that the product ID is not none
        self.assertIsNotNone(product.id)
        # Fetch the product back from the db
        db_product = Product.find(product.id)
        # Assert the properties of the db product
        self.assertEqual(db_product.id, product.id)
        self.assertEqual(db_product.name, product.name)
        self.assertEqual(db_product.description, product.description)
        self.assertEqual(db_product.price, product.price)
        self.assertEqual(db_product.category, product.category)

    def test_update_a_product(self):
        """Test case to update a product"""
        product = ProductFactory()
        logging.info(str(product))
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Change product description
        product.description = "test description"
        # Get the original product's ID
        original_id = product.id
        # Update the product in the db
        product.update()
        # Assert that ID remains the same but description changes
        self.assertEqual(original_id, product.id)
        self.assertEqual(product.description, "test description")
        # Fetch all products back
        products = Product.all()
        # Assert that there is only one product
        self.assertEqual(len(products), 1)
        # Assert that the fetched product has the same ID and the updated description
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "test description")

    def test_delete_a_product(self):
        """Test case to delete a product"""
        product = ProductFactory()
        product.create()
        # Assert that there is only one product in the db
        self.assertEqual(len(Product.all()), 1)
        # Delete the product
        product.delete()
        # Assert that the db is empty after deletion
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """Test to list all products in the db"""
        products = Product.all()
        # Assert that there are no products in the db at the beginning
        self.assertEqual(len(products), 0)
        # Create products and save them to the db
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # Assert that there are 5 items in the db
        self.assertEqual(len(Product.all()), 5)

    def test_find_by_name(self):
        """Test to find products by their name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        # Get the name of the first product
        name = products[0].name
        # Count the number of occurrences of this name
        count = len([product for product in products if product.name == name])
        # Retrieve all products that share this name
        found = Product.find_by_name(name)
        # Assert that count matches the expected number of products with this name
        self.assertEqual(found.count(), count)
        # Assert that each product name matches the expected name
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """Test to find products based on availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Retrieve availability of the first product
        available = products[0].available
        # Retrieve the number of products with the same availability
        count = len([product for product in products if product.available == available])
        # Retrieve products with the same availability
        found = Product.find_by_availability(available)
        # Assert that the count of the found products matches the expected count
        self.assertEqual(found.count(), count)
        # Assert that each product's availability matches the expected availability
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """Test to find products based on category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Retrieve the category of the first product in the db
        category = products[0].category
        # Check the number of products that share the same category
        count = len([product for product in products if product.category == category])
        # Retrieve all products with the specified category
        found = Product.find_by_category(category)
        # Assert that the count of the found products matches the expected count
        self.assertEqual(found.count(), count)
        # Assert that each product's category matches the expected category
        for product in found:
            self.assertEqual(product.category, category)
