from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Panchang
from .services import get_panchang


class PanchangEndpointsTests(APITestCase):
	def test_today_panchang_fetches_and_caches_when_missing(self):
		self.assertEqual(Panchang.objects.count(), 0)

		with patch("astrology.views.get_panchang", return_value={"tithi": "Test"}):
			response = self.client.get("/api/astrology/panchang/today/")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertFalse(response.data["cached"])
		self.assertIn("panchang", response.data)
		self.assertEqual(Panchang.objects.count(), 1)

	def test_current_date_returns_panchang_data_when_db_is_empty(self):
		self.assertEqual(Panchang.objects.count(), 0)

		with patch("astrology.views.get_panchang", return_value={"nakshatra": "Test"}):
			response = self.client.get("/api/astrology/current-date/")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn("panchang", response.data)
		self.assertIsNotNone(response.data["panchang"])
		self.assertEqual(Panchang.objects.count(), 1)


class PanchangServiceSandboxFallbackTests(APITestCase):
	def test_get_panchang_falls_back_to_jan_1_in_sandbox(self):
		class FakeResponse:
			def __init__(self, status_code, payload):
				self.status_code = status_code
				self._payload = payload
				self.text = str(payload)

			def json(self):
				return self._payload

		with patch("astrology.services.get_access_token", return_value="token"):
			with patch("astrology.services.requests.get") as mock_get:
				mock_get.side_effect = [
					FakeResponse(
						400,
						{
							"errors": [
								{
									"detail": "In sandbox mode, only January 1st is allowed - any time and any year is accepted.",
								}
							]
						},
					),
					FakeResponse(200, {"data": {"tithi": "Test"}}),
				]

				result = get_panchang("2026-04-27")

		self.assertEqual(mock_get.call_count, 2)
		first_call_datetime = mock_get.call_args_list[0].kwargs["params"]["datetime"]
		second_call_datetime = mock_get.call_args_list[1].kwargs["params"]["datetime"]
		self.assertEqual(first_call_datetime, "2026-04-27T06:00:00+05:45")
		self.assertEqual(second_call_datetime, "2026-01-01T06:00:00+05:45")
		self.assertTrue(result["_sandbox_fallback"]["active"])
		self.assertEqual(result["_sandbox_fallback"]["requested_date"], "2026-04-27")
		self.assertEqual(result["_sandbox_fallback"]["used_date"], "2026-01-01")
