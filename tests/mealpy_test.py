import pytest
import requests
import responses

from mealpy import mealpy


@pytest.fixture(autouse=True)
def mock_responses():
    with responses.RequestsMock() as _responses:
        yield _responses


class TestGetCity:

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
