# ----------------------------------------------------------------------------
# Copyright (C) 2021-2022 Deepchecks (https://www.deepchecks.com)
#
# This file is part of Deepchecks.
# Deepchecks is distributed under the terms of the GNU Affero General
# Public License (version 3 or later).
# You should have received a copy of the GNU Affero General Public License
# along with Deepchecks.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------
#
"""Module for calculating the properties used in Vision checks."""
import warnings
from enum import Enum

__all__ = ['PropertiesInputType', 'validate_properties']

from typing import List, Dict, Any

from deepchecks.core.errors import DeepchecksValueError


class PropertiesInputType(Enum):
    """Enum containing supported task types."""

    IMAGES = 'images'
    BBOXES = 'bounding_boxes'
    LABELS = 'labels'
    PREDICTIONS = 'predictions'
    OTHER = 'other'

def calc_vision_properties(raw_data, properties_list) -> Dict[str, list]:
    """
    Calculates the image properties for a batch of images.

    Parameters
    ----------
    raw_data : torch.Tensor
        Batch of images to transform to image properties.

    vision_properties: List[Dict] , default: None
        A list of properties to calculate

    Returns
    ------
    batch_properties: dict[str, List]
        A dict of property name, property value per sample
    """

    batch_properties = defaultdict(list)
    for single_property in properties_list:
        property_list = single_property['method'](raw_data)
        batch_properties[single_property['name']] = property_list
    return batch_properties


def validate_properties(properties: List[Dict[str, Any]]):
    """Validate structure of measurements."""
    if not isinstance(properties, list):
        raise DeepchecksValueError(
            'Expected properties to be a list, '
            f'instead got {type(properties).__name__}'
        )

    if len(properties) == 0:
        raise DeepchecksValueError('Properties list can\'t be empty')

    expected_keys = ('name', 'method', 'output_type')
    deprecated_output_types = ('discrete', 'continuous')
    output_types = ('categorical', 'numerical')

    list_of_warnings = []
    errors = []

    for index, image_property in enumerate(properties):

        if not isinstance(image_property, dict):
            errors.append(
                f'Item #{index}: property must be of type dict, '
                f'and include keys {expected_keys}. Instead got {type(image_property).__name__}'
            )
            continue

        property_name = image_property.get('name') or f'#{index}'
        difference = sorted(set(expected_keys).difference(set(image_property.keys())))

        if len(difference) > 0:
            errors.append(
                f'Property {property_name}: dictionary must include keys {expected_keys}. '
                f'Next keys are missed {difference}'
            )
            continue

        property_output_type = image_property['output_type']

        if property_output_type in deprecated_output_types:
            list_of_warnings.append(
                f'Property {property_name}: output types {deprecated_output_types} are deprecated, '
                f'use instead {output_types}'
            )
        elif property_output_type not in output_types:
            errors.append(
                f'Property {property_name}: field "output_type" must be one of {output_types}, '
                f'instead got {property_output_type}'
            )

    if len(errors) > 0:
        errors = '\n+ '.join(errors)
        raise DeepchecksValueError(f'List of properties contains next problems:\n+ {errors}')

    if len(list_of_warnings) > 0:
        concatenated_warnings = '\n+ '.join(list_of_warnings)
        warnings.warn(
            f'Property Warnings:\n+ {concatenated_warnings}',
            category=DeprecationWarning
        )

    return properties