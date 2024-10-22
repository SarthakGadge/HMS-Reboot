from django_filters import rest_framework as filters
from .models import Room
import django_filters


class RoomFilter(filters.FilterSet):
    rent = filters.NumberFilter(
        field_name="rent", lookup_expr='exact')  # Exact rent amount
    min_rent = filters.NumberFilter(
        field_name="rent", lookup_expr='gte')  # Minimum rent
    max_rent = filters.NumberFilter(
        field_name="rent", lookup_expr='lte')  # Maximum rent

    occupancy = filters.NumberFilter(
        field_name="occupancy", lookup_expr='exact')  # Exact occupancy count
    min_occupancy = filters.NumberFilter(
        field_name="occupancy", lookup_expr='gte')  # Minimum occupancy
    max_occupancy = filters.NumberFilter(
        field_name="occupancy", lookup_expr='lte')  # Maximum occupancy

    vacancy = filters.NumberFilter(
        field_name="vacancy", lookup_expr='exact')  # Exact vacancy count
    min_vacancy = filters.NumberFilter(
        field_name="vacancy", lookup_expr='gte')  # Minimum vacancy
    max_vacancy = filters.NumberFilter(
        field_name="vacancy", lookup_expr='lte')  # Maximum vacancy

    amenities = filters.BaseInFilter(
        field_name='amenities__id', lookup_expr='in')

    class Meta:
        model = Room
        fields = ['rent', 'min_rent', 'max_rent', 'occupancy', 'min_occupancy',
                  'max_occupancy', 'vacancy', 'min_vacancy', 'max_vacancy']
