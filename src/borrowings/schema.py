from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
    OpenApiTypes,
)
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    BorrowingDetailSerializer,
)


borrowings_schema_view = extend_schema_view(
    list=extend_schema(
        summary="List Borrowings",
        description=(
            "Retrieve a list of borrowing records. "
            "This endpoint supports filtering via query parameters. "
            "The 'is_active' parameter accepts 'true' to filter for borrowings with a pending or overdue status, "
            "and 'false' to filter for returned borrowings. "
            "The 'user_id' parameter filters the records by the specified user ID, available to superusers or if it matches the current user's ID."
        ),
        parameters=[
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.STR,
                description=(
                    "Filter borrowings by active status. Use 'true' to return pending/overdue records, "
                    "or 'false' to return returned records."
                ),
                required=False,
                examples=[
                    OpenApiExample("Active Borrowings", value="true"),
                    OpenApiExample("Returned Borrowings", value="false"),
                ],
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                description=(
                    "Filter borrowings by user ID. This is applicable only if the authenticated user is a superuser or "
                    "if the specified user ID matches that of the authenticated user."
                ),
                required=False,
                examples=[
                    OpenApiExample("Filter by User ID", value=1),
                ],
            ),
        ],
        responses=OpenApiResponse(
            response=BorrowingListSerializer,
            description="A list of borrowing records.",
            examples=[
                OpenApiExample(
                    "Example Response",
                    value=[
                        {
                            "id": 1,
                            "user_email": "user@example.com",
                            "book_title": "The Great Gatsby",
                            "book_authors": [{"id": 1, "name": "F. Scott Fitzgerald"}],
                            "borrow_date": "2025-03-03",
                            "expected_return_date": "2025-03-10",
                            "status": "pending",
                        }
                    ],
                )
            ],
        ),
    ),
    retrieve=extend_schema(
        summary="Retrieve Borrowing",
        description=(
            "Retrieve detailed information for a specific borrowing record by its ID. "
            "The detailed response includes information about the associated book and the user."
        ),
        responses=OpenApiResponse(
            response=BorrowingDetailSerializer,
            description="Detailed borrowing record information.",
            examples=[
                OpenApiExample(
                    "Example Response",
                    value={
                        "id": 1,
                        "user_email": "user@example.com",
                        "book": {
                            "id": 1,
                            "title": "The Great Gatsby",
                            "authors": [{"id": 1, "name": "F. Scott Fitzgerald"}],
                            "inventory": 5,
                            "description": "A classic novel.",
                        },
                        "borrow_date": "2025-03-03",
                        "expected_return_date": "2025-03-10",
                        "actual_return_date": "2025-03-09",
                        "status": "returned",
                    },
                )
            ],
        ),
    ),
    create=extend_schema(
        summary="Create Borrowing",
        description=(
            "Create a new borrowing record after validating the availability of the book, "
            "ensuring the expected return date is valid, and confirming that the user doesn't already have an active borrowing for this book. "
            "Upon successful creation, the book's inventory is decremented by one."
        ),
        request=BorrowingCreateSerializer,
        responses=OpenApiResponse(
            response=BorrowingCreateSerializer,
            description="The newly created borrowing record.",
            examples=[
                OpenApiExample(
                    "Example Request",
                    value={
                        "book": 1,
                        "expected_return_date": "2025-03-10",
                    },
                ),
                OpenApiExample(
                    "Example Response",
                    value={
                        "id": 1,
                        "book": 1,
                        "expected_return_date": "2025-03-10",
                    },
                ),
            ],
        ),
    ),
    return_book=extend_schema(
        summary="Return Book",
        description=(
            "Mark a borrowing record as returned. If the borrowing is already returned, an error message is returned. "
            "Otherwise, the borrowing's status is updated, the actual return date is set automatically to the current date, "
            "and the associated book's inventory is incremented by one."
        ),
        responses={
            200: OpenApiResponse(
                description="Borrowing returned successfully.",
                examples=[
                    OpenApiExample(
                        "Success Example",
                        value={"message": "Borrowing returned successfully"},
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Borrowing is already returned.",
                examples=[
                    OpenApiExample(
                        "Error Example",
                        value={"message": "Borrowing is already returned"},
                    )
                ],
            ),
        },
    ),
)
