from rest_framework.test import APITestCase
from . import models


class TestAmenities(APITestCase):

    NAME = "Amenity Test"
    DESC = "Amenity Des"

    URL = "/api/v1/rooms/amenities/"

    def setUp(self):
        models.Amenity.objects.create(
            name=self.NAME,
            description=self.DESC,
        )

    def test_all_amenities(self):

        response = self.client.get(self.URL)
        data = response.json()

        self.assertEqual(
            response.status_code,
            200,
            "Status code isn't 200",
        )

        self.assertIsInstance(
            data,
            list,
        )
        self.assertEqual(
            len(data),
            1,
        )
        self.assertEqual(
            data[0]["name"],
            self.NAME,
        )
        self.assertEqual(
            data[0]["description"],
            self.DESC,
        )

    def test_create_amenity(self):

        new_amenity_name = "New Amenity"
        new_amenity_description = "New Amenity desc."

        response = self.client.post(
            self.URL,
            data={
                "name": new_amenity_name,
                "description": new_amenity_description,
            },
        )

        data = response.json()

        self.assertEqual(
            response.status_code,
            200,
            "Not 200 status code",
        )
        self.assertEqual(
            data["name"],
            new_amenity_name,
            "amenity name is different",
        )
        self.assertEqual(
            data["description"],
            new_amenity_description,
            "amenity description is different",
        )

        response = self.client.post(self.URL)
        data = response.json()

        self.assertEqual(
            response.status_code,
            400,
            "status code isn't 400",
        )
        self.assertIn(
            "name",
            data,
            "there is no name in the data",
        )


class TestAmenity(APITestCase):

    NAME = "Test Amenity"
    DESC = "Test Dsc"

    def setUp(self):
        models.Amenity.objects.create(
            name=self.NAME,
            description=self.DESC,
        )

    def test_amenity_not_found(self):

        response = self.client.get("/api/v1/rooms/amenities/2")

        self.assertEqual(response.status_code, 404, "status code is not 404")

    def test_get_amenity(self):

        response = self.client.get("/api/v1/rooms/amenities/1")

        self.assertEqual(response.status_code, 200, "status code is not 200")

        data = response.json()

        self.assertEqual(
            data["name"],
            self.NAME,
            "name is not same",
        )
        self.assertEqual(
            data["description"],
            self.DESC,
            "description is not same",
        )

    def test_put_amenity(self):

        updated_amenity_name = "updated name"
        updated_amenity_description = "updated description"

        response = self.client.put(
            "/api/v1/rooms/amenities/1",
            data={
                "name": updated_amenity_name,
                "description": updated_amenity_description,
            },
        )

        data = response.json()

        self.assertEqual(
            response.status_code,
            200,
            "status code is not 200",
        )
        self.assertEqual(
            data["name"],
            updated_amenity_name,
            "updated name is not same",
        )
        self.assertEqual(
            data["description"],
            updated_amenity_description,
            "description is not same",
        )

        long_amenity_name = "asdjfakpsodfjapsdofjaspdofiajspodfiajsdpfioasjdfpasiodjfpasdifjapsdfiojaspdfioasjdpfoaisjdfpaosidfjpasodifjapsdofijaspdfiojaspdfoijaspdfoijaspdfiajsdadasdfa"
        long_amenity_description = "asdjfakpsodfjapsdofjaspdofiajspodfiajsdpfioasjdfpasiodjfpasdifjapsdfiojaspdfioasjdpfoaisjdfpaosidfjpasodifjapsdofijaspdfiojaspdfoijaspdfoijaspdfiajsdadasdfa"

        response = self.client.put(
            "/api/v1/rooms/amenities/1",
            data={
                "name": long_amenity_name,
                "description": long_amenity_description,
            },
        )

        self.assertEqual(
            response.status_code,
            400,
            "status code is not 200",
        )

    def test_delete_amenity(self):

        response = self.client.delete("/api/v1/rooms/amenities/1")

        self.assertEqual(response.status_code, 204, "status code is not 204")
