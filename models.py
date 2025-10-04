from pydantic import BaseModel
from typing import List, Optional


class HelloResponse(BaseModel):
    """Response model for /hello endpoint"""

    Message: str


class ActionMapping(BaseModel):
    """Mapping configuration for action fields"""

    key: str
    label: str
    value: str


class Action(BaseModel):
    """Action configuration"""

    key: str
    label: str
    iconSvgBase64: str
    metaEndpoint: str
    mappings: List[ActionMapping]


class ConfigurationFormField(BaseModel):
    """Configuration form field"""

    key: str
    label: str
    required: bool
    type: str
    sensitive: Optional[bool] = None
    useAsHttpHeader: str
    description: Optional[str] = None
    placeholder: Optional[str] = None


class ConfigResponse(BaseModel):
    """Response model for / (config) endpoint"""

    version: str
    name: str
    logoBase64: str
    actions: List[Action]
    webhookProcessEndpoint: str
    webhookAuthenticationHeader: str
    configurationFormFields: List[ConfigurationFormField]


class SelectOption(BaseModel):
    """Single select option"""

    label: str
    value: str


class FormField(BaseModel):
    """Form field configuration"""

    key: str
    label: str
    type: str
    required: Optional[bool]
    readonly: Optional[bool]
    includeValueInRefetch: Optional[bool]
    placeholder: Optional[str]
    value: Optional[str]
    singleSelectOptions: Optional[List[SelectOption]]
    intent: Optional[str]
    description: Optional[str]


class ExportResponse(BaseModel):
    """Response model for /export endpoint"""

    actionVersion: str
    key: str
    label: str
    description: str
    formFields: List[FormField]
    submitEndpoint: str


class ExternalLink(BaseModel):
    """External link configuration"""

    key: str
    label: str
    url: str


class Toast(BaseModel):
    """Toast notification"""

    error: Optional[str] = None


class CreateAssessmentSuccessResponse(BaseModel):
    """Success response model for /create_assessment endpoint"""

    resultVersion: str
    key: str
    success: bool
    assessmentName: str
    message: str
    status: str
    externalIdentifier: str
    externalRecordUrl: str
    externalLinks: List[ExternalLink]


class CreateAssessmentErrorResponse(BaseModel):
    """Error response model for /create_assessment endpoint"""

    resultVersion: str
    key: str
    success: bool
    toast: Toast


class AssessmentUpdate(BaseModel):
    """Assessment update object"""

    externalIdentifier: str
    status: str
    score: int
    shouldNotify: bool
    externalLinks: List[ExternalLink]


class WebhookResponse(BaseModel):
    """Response model for /webhook endpoint"""

    resultVersion: str
    success: bool
    updateAssessments: List[AssessmentUpdate]
