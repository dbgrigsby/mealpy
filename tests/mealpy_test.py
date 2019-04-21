from collections import namedtuple

import pytest
import requests
import responses

from mealpy import mealpy

City = namedtuple('City', 'name objectId')


@pytest.fixture(autouse=True)
def mock_responses():
    with responses.RequestsMock() as _responses:
        yield _responses


class TestCity:

    @staticmethod
    def test_get_city(mock_responses):
        response = {
            'result': [
                {
                    'id': 'mock_id1',
                    'objectId': 'mock_objectId1',
                    'state': 'CA',
                    'name': 'San Francisco',
                    'city_code': 'SFO',
                    'latitude': 'mock_latitude',
                    'longitude': 'mock_longitude',
                    'timezone': -7,
                    'countryCode': 'usa',
                    'countryCodeAlphaTwo': 'us',
                    'defaultLocale': 'en-US',
                    'dinner': False,
                    'neighborhoods': [
                        {
                            'id': 'mock_fidi_id',
                            'name': 'Financial District',
                        },
                        {
                            'id': 'mock_soma_id',
                            'name': 'SoMa',
                        },
                    ],
                },
                {
                    'id': 'mock_id2',
                    'objectId': 'mock_objectId2',
                    'state': 'WA',
                    'name': 'Seattle',
                    'city_code': 'SEA',
                    'latitude': 'mock_latitude',
                    'longitude': 'mock_longitude',
                    'timezone': -7,
                    'countryCode': 'usa',
                    'countryCodeAlphaTwo': 'us',
                    'defaultLocale': 'en-US',
                    'dinner': False,
                    'neighborhoods': [
                        {
                            'id': 'mock_belltown_id',
                            'name': 'Belltown',
                        },
                    ],
                },
            ],
        }

        mock_responses.add(
            responses.RequestsMock.POST,
            mealpy.CITIES_URL,
            json=response,
        )

        mealpal = mealpy.MealPal()
        city = mealpal.get_city('San Francisco')

        assert city.items() >= {
            'id': 'mock_id1',
            'state': 'CA',
            'name': 'San Francisco',
        }.items()

    @staticmethod
    def test_get_city_not_found(mock_responses):
        response = {
            'result': [
                {
                    'id': 'mock_id1',
                    'objectId': 'mock_objectId1',
                    'state': 'CA',
                    'name': 'San Francisco',
                    'city_code': 'SFO',
                },
            ],
        }

        mock_responses.add(
            responses.RequestsMock.POST,
            mealpy.CITIES_URL,
            json=response,
        )

        mealpal = mealpy.MealPal()
        city = mealpal.get_city('Not San Francisco')

        assert not city

    @staticmethod
    def test_get_city_bad_response(mock_responses):
        mock_responses.add(
            responses.RequestsMock.POST,
            mealpy.CITIES_URL,
            status=400,
        )

        mealpal = mealpy.MealPal()
        with pytest.raises(requests.exceptions.HTTPError):
            mealpal.get_city('Not San Francisco')


class TestLogin:

    @staticmethod
    def test_login(mock_responses):
        mock_responses.add(
            responses.RequestsMock.POST,
            mealpy.LOGIN_URL,
            status=200,
            json={
                'id': 'GUID',
                'email': 'email',
                'status': 3,
                'firstName': 'first_name',
                'lastName': 'last_name',
                'sessionToken': 'r:GUID',
                'city': {
                    'id': 'GUID',
                    'name': 'San Francisco',
                    'city_code': 'SFO',
                    'countryCode': 'usa',
                    '__type': 'Pointer',
                    'className': 'City',
                    'objectId': 'GUID',
                },
            },
        )

        mealpal = mealpy.MealPal()

        assert mealpal.login('username', 'password') == 200

    @staticmethod
    def test_login_fail(mock_responses):
        mock_responses.add(
            method=responses.RequestsMock.POST,
            url=mealpy.LOGIN_URL,
            status=404,
            json={
                'code': 101,
                'error': 'An error occurred while blah blah, try agian.',
            },
        )

        mealpal = mealpy.MealPal()

        with pytest.raises(requests.HTTPError):
            mealpal.login('username', 'password')


class TestSchedule:

    @staticmethod
    @pytest.fixture
    def mock_city():
        yield City('mock_city', 'mock_city_object_id')

    @staticmethod
    @pytest.fixture
    def success_response():
        """A complete response example for MENU_URL endpoint."""
        yield {
            'city': {
                'id': 'GUID',
                'name': 'San Francisco',
                'state': 'CA',
                'time_zone_name': 'America/Los_Angeles',
            },
            'generated_at': '2019-04-01T00:00:00Z',
            'schedules': [{
                'id': 'GUID',
                'priority': 9,
                'is_featured': True,
                'date': '20190401',
                'meal': {
                    'id': 'GUID',
                    'name': 'Spam and Eggs',
                    'description': 'Soemthign sometlhing python',
                    'cuisine': 'asian',
                    'image': 'https://example.com/image.jpg',
                    'portion': 2,
                    'veg': False,
                },
                'restaurant': {
                    'id': 'GUID',
                    'name': 'RestaurantName',
                    'address': 'RestaurantAddress',
                    'state': 'CA',
                    'latitude': '111.111',
                    'longitude': '-111.111',
                    'neighborhood': {
                        'name': 'Financial District',
                        'id': 'GUID',
                    },
                    'city': {
                        'name': 'San Francisco',
                        'id': 'GUID',
                        'timezone_offset_hours': -7,
                    },
                    'open': '2019-04-01T00:00:00Z',
                    'close': '2019-04-01T00:00:00Z',
                    'mpn_open': '2019-04-01T00:00:00Z',
                    'mpn_close': '2019-04-01T00:00:00Z',
                },
            }],
        }

    @staticmethod
    @pytest.fixture
    def menu_url_response(mock_responses, success_response, mock_city):
        mock_responses.add(
            responses.RequestsMock.GET,
            mealpy.MENU_URL.format(mock_city.objectId),
            status=200,
            json=success_response,
        )

        yield mock_responses

    @staticmethod
    @pytest.fixture
    def mock_get_city(mock_responses, mock_city):
        mock_responses.add(
            method=responses.RequestsMock.POST,
            url=mealpy.CITIES_URL,
            json={
                'result': [{
                    'id': 'mock_id1',
                    'objectId': mock_city.objectId,
                    'name': mock_city.name,
                }],
            },
        )
        yield

    @staticmethod
    @pytest.mark.usefixtures('mock_get_city', 'menu_url_response')
    def test_get_schedule_by_restaurant_name(mock_city):
        mealpal = mealpy.MealPal()

        schedule = mealpal.get_schedule_by_restaurant_name('RestaurantName', mock_city.name)

        meal = schedule['meal']
        restaurant = schedule['restaurant']

        assert meal.items() >= {
            'id': 'GUID',
            'name': 'Spam and Eggs',
        }.items()

        assert restaurant.items() >= {
            'id': 'GUID',
            'name': 'RestaurantName',
            'address': 'RestaurantAddress',
        }.items()

    @staticmethod
    @pytest.mark.usefixtures('mock_get_city', 'menu_url_response')
    def test_get_schedule_by_restaurant_name_not_found(mock_city):
        mealpal = mealpy.MealPal()

        # TODO(#24):  Handle invalid restaurant
        with pytest.raises(StopIteration):
            mealpal.get_schedule_by_restaurant_name('NotFound', mock_city.name)

    @staticmethod
    @pytest.mark.usefixtures('mock_get_city', 'menu_url_response')
    def test_get_schedule_by_meal_name_not_found(mock_city):
        mealpal = mealpy.MealPal()

        # TODO(#24):  Handle invalid restaurant
        with pytest.raises(StopIteration):
            mealpal.get_schedule_by_meal_name('NotFound', mock_city.name)

    @staticmethod
    @pytest.mark.usefixtures('mock_get_city', 'menu_url_response')
    def test_get_schedule_by_meal_name(mock_city):
        mealpal = mealpy.MealPal()

        schedule = mealpal.get_schedule_by_meal_name('Spam and Eggs', mock_city.name)

        meal = schedule['meal']
        restaurant = schedule['restaurant']

        assert meal.items() >= {
            'id': 'GUID',
            'name': 'Spam and Eggs',
        }.items()

        assert restaurant.items() >= {
            'id': 'GUID',
            'name': 'RestaurantName',
            'address': 'RestaurantAddress',
        }.items()

    @staticmethod
    @pytest.mark.usefixtures('mock_get_city')
    def test_get_schedules_fail(mock_responses, mock_city):
        mock_responses.add(
            method=responses.RequestsMock.GET,
            url=mealpy.MENU_URL.format(mock_city.objectId),
            status=400,
        )

        mealpal = mealpy.MealPal()

        with pytest.raises(requests.HTTPError):
            mealpal.get_schedules(mock_city.name)


class TestCurrentMeal:

    @staticmethod
    @pytest.fixture
    def current_meal():
        yield {
            'id': 'GUID',
            'createdAt': '2019-03-20T02:53:28.908Z',
            'date': 'March 20, 2019',
            'pickupTime': '12:30-12:45',
            'pickupTimeIso': ['12:30', '12:45'],
            'googleCalendarLink': (
                'https://www.google.com/calendar/render?action=TEMPLATE&text=Pick Up Lunch from MealPal&'
                'details=Pick up lunch from MealPal: MEALNAME from RESTAURANTNAME\nPickup instructions: BLAHBLAH&'
                'location=ADDRESS, CITY, STATE&dates=20190320T193000Z/20190320T194500Z&sf=true&output=xml'
            ),
            'mealpalNow': False,
            'orderNumber': '1111',
            'emojiWord': None,
            'emojiCharacter': None,
            'emojiUrl': None,
            'meal': {
                'id': 'GUID',
                'image': 'https://example.com/image.jpg',
                'description': 'spam, eggs, and bacon. Served on avocado toast. With no toast.',
                'name': 'Spam Eggs',
            },
            'restaurant': {
                'id': 'GUID',
                'name': 'RESTURANTNAME',
                'address': 'ADDRESS',
                'city': {
                    '__type': 'Object',
                    'className': 'cities',
                    'createdAt': '2016-06-22T14:33:23.000Z',
                    'latitude': '111.111',
                    'longitude': '-111.111',
                    'name': 'San Francisco',
                    'city_code': 'SFO',
                    'objectId': 'GUID',
                    'state': 'CA',
                    'timezone': -7,
                    'updatedAt': '2019-03-18T16:08:22.577Z',
                },
                'latitude': '111.1111',
                'longitude': '-111.1111',
                'lunchOpen': '11:30am',
                'lunchClose': '2:30pm',
                'pickupInstructions': 'BLAH BLAH',
                'state': 'CA',
                'timezoneOffset': -7,
                'neighborhood': {
                    'id': 'GUID',
                    'name': 'SoMa',
                },
            },
            'schedule': {
                '__type': 'Object',
                'objectId': 'GUID',
                'className': 'schedules',
                'date': {
                    '__type': 'Date',
                    'iso': '2019-03-20T00:00:00.000Z',
                },
            },
        }

    @staticmethod
    @pytest.fixture
    def success_response_no_reservation():
        yield {
            'result': {
                'status': 'OPEN',
                'kitchenMode': 'classic',
                'time': '19:59',
                'reserveUntil': '2019-03-20T10:30:00-07:00',
                'cancelUntil': '2019-03-20T15:00:00-07:00',
                'kitchenTimes': {
                    'openTime': '5pm',
                    'openTimeMilitary': 1700,
                    'openHourMilitary': 17,
                    'openMinutesMilitary': 0,
                    'openHour': '5',
                    'openMinutes': '00',
                    'openPeriod': 'pm',
                    'closeTime': '10:30am',
                    'closeTimeMilitary': 1030,
                    'closeHourMilitary': 10,
                    'closeMinutesMilitary': 30,
                    'closeHour': '10',
                    'closeMinutes': '30',
                    'closePeriod': 'am',
                    'lateCancelHour': 15,
                    'lateCancelMinutes': 0,
                },
                'today': {
                    '__type': 'Date',
                    'iso': '2019-03-20T02:59:42.000Z',
                },
            },
        }

    @staticmethod
    @pytest.fixture
    def kitchen_url_response(mock_responses, success_response_no_reservation):
        mock_responses.add(
            responses.RequestsMock.POST,
            mealpy.KITCHEN_URL,
            status=200,
            json=success_response_no_reservation,
        )

        yield mock_responses

    @staticmethod
    @pytest.fixture
    def kitchen_url_response_with_reservation(mock_responses, success_response_no_reservation, current_meal):
        success_response_no_reservation['reservation'] = current_meal

        mock_responses.add(
            responses.RequestsMock.POST,
            mealpy.KITCHEN_URL,
            status=200,
            json=success_response_no_reservation,
        )

        yield mock_responses

    @staticmethod
    @pytest.mark.usefixtures('kitchen_url_response')
    def test_get_current_meal_no_meal():
        mealpal = mealpy.MealPal()

        current_meal = mealpal.get_current_meal()

        assert 'reservation' not in current_meal

    @staticmethod
    @pytest.mark.usefixtures('kitchen_url_response_with_reservation')
    def test_get_current_meal():
        mealpal = mealpy.MealPal()

        current_meal = mealpal.get_current_meal()

        assert current_meal['reservation'].keys() >= {
            'id',
            'pickupTime',
            'orderNumber',
            'meal',
            'restaurant',
            'schedule',
        }

    @staticmethod
    def test_cancel_current_meal():
        mealpal = mealpy.MealPal()
        with pytest.raises(NotImplementedError):
            mealpal.cancel_current_meal()
