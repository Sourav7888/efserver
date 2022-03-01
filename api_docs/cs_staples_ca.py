schema = {
    "swagger": "2.0",
    "info": {
        "description": "Staples Sustainability Project Project Pre-Approved API",
        "version": "1.0.0",
        "title": "Staples Sustainability Project -  External API",
        "contact": {"email": "tantely.raza@enerfrog.com"},
    },
    "host": "staples-api.enerfrog.ca/",
    "tags": [  # This is where you describe the main container of each API
        {
            "name": "Waste Manager",
            "description": "Waste Data & Analytics",
        },
    ],
    "schemes": ["https"],
    "paths": {
        "/v1/etl/sustainability/waste/total-by-waste-category/": {
            "get": {
                "tags": ["Waste Manager"],
                "summary": "Get the total waste per category - This is a public endpoint and will not require authentication.",
                "description": "",
                "operationId": "getTotalWastePerCategory",
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "division",
                        "in": "query",
                        "description": "The division to which to get the total from: ",
                        "required": "true",
                        "type": "string",
                        "format": "string",
                        "enum": [
                            "Staples Retail",
                            "Staples Professional",
                            "Staples CA - Warehouses",
                        ],
                    },
                    {
                        "name": "waste_category",
                        "in": "query",
                        "description": "The waste category to which to get the total from:",
                        "required": "false",
                        "type": "string",
                        "format": "string",
                        "enum": [
                            "ink-toner",
                            "styrofoam",
                            "writing-instruments",
                            "pallets",
                            "general-waste",
                            "regulated-substances",
                            "batteries",
                            "electronics",
                        ],
                    },
                    {
                        "name": "diversion",
                        "in": "query",
                        "description": "Only set to true when querying for styrofoam and regulated-substances, otherwise leave blank or set to false.",
                        "type": "boolean",
                    },
                    {
                        "name": "min_date",
                        "in": "query",
                        "description": "Minimum date to start the total calculation from. Format: YYYY-MM-DD",
                        "type": "string",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "successful operation",
                        "schema": {"$ref": "#/definitions/TotalPerWasteCategory"},
                    }
                },
            }
        },
    },
    "securityDefinitions": {
        "api_key": {"type": "apiKey", "name": "Authorization", "in": "header"},
    },
    "definitions": {
        "TotalPerWasteCategory": {
            "type": "object",
            "properties": {
                "total": {"type": "number", "format": "float"},
            },
        },
    },
}
