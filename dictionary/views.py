import difflib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import LexicalEntry, Lemma, Definition, Context
from .serializers import LexicalEntrySerializer
from .utils import has_diacritics, remove_diacritics, normalize_for_variations, QuerysetFilter
from rest_framework.pagination import PageNumberPagination
from .serializers import PhraseSearchQuerySerializer, RootSearchQuerySerializer, DictionaryRetrieveQuerySerializer

class DictionaryRetrieveAPIView(APIView):
    """
    API for retrieving lexical entries by query, with filtering, pagination,
    support for diacritics, spelling variations, and suggestions.
    """

    @swagger_auto_schema(
        query_serializer=DictionaryRetrieveQuerySerializer,
        responses={
            200: openapi.Response(
                description="Filtered, paginated search results by query.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of results."),
                        "next": openapi.Schema(type=openapi.TYPE_STRING, description="URL for the next page of results."),
                        "previous": openapi.Schema(type=openapi.TYPE_STRING, description="URL for the previous page of results."),
                        "results": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
            404: openapi.Response(
                description="No matches found",
                examples={
                    "application/json": {
                        "message": "No matches found for 'كتبة'."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "Query parameter is required."
                    }
                }
            ),
        },
    )
    def get(self, request):
        # Step 1: Validate query parameters
        serializer = DictionaryRetrieveQuerySerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        query_params = serializer.validated_data

        query = query_params.get('query', '').strip()
        if not query:
            return Response({'error': 'Query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        contains_diacritics = has_diacritics(query)

        # Step 2: Match with diacritics
        if contains_diacritics:
            lexical_entries = LexicalEntry.objects.filter(lemma__written_form=query)
            if lexical_entries.exists():
                return self._paginate_and_respond(lexical_entries, query_params, request)

            # Match without diacritics
            stripped_query = remove_diacritics(query)
            lexical_entries = LexicalEntry.objects.filter(lemma__written_form__icontains=stripped_query)
            if lexical_entries.exists():
                return self._paginate_and_respond(lexical_entries, query_params, request)

        # Step 3: Match non-diacritized queries on LexicalEntry.id
        if not contains_diacritics:
            lexical_entries = LexicalEntry.objects.filter(id=query)
            if lexical_entries.exists():
                return self._paginate_and_respond(lexical_entries, query_params, request)

        # Step 4: Apply spelling variations if no matches
        normalized_query = normalize_for_variations(remove_diacritics(query))
        lexical_entries = LexicalEntry.objects.filter(
            Q(lemma__written_form__icontains=normalized_query) | Q(id=normalized_query)
        ).distinct()
        if lexical_entries.exists():
            return self._paginate_and_respond(lexical_entries, query_params, request)

        # Step 5: Provide suggestions if no matches
        return self._provide_suggestions(query)

    def _paginate_and_respond(self, queryset, query_params, request):
        """
        Helper method to apply filters, paginate results, and return the response.
        """
        # Apply filters
        filtered_entries = QuerysetFilter(queryset).apply_filters(query_params)

        # Paginate results
        paginator = PageNumberPagination()
        paginator.page_size_query_param = 'page_size'
        paginator.page_size = 50  # Default page size
        paginator.max_page_size = 100
        paginated_entries = paginator.paginate_queryset(filtered_entries, request)

        # Serialize and return paginated results
        serializer = LexicalEntrySerializer(paginated_entries, many=True)
        return paginator.get_paginated_response(serializer.data)

    def _provide_suggestions(self, query):
        """
        Provide suggestions for the query if no matches are found.
        """
        all_lemmas = Lemma.objects.values_list('written_form', flat=True)
        stripped_lemmas = {remove_diacritics(lemma): lemma for lemma in all_lemmas}

        # Find close matches using difflib
        suggestions = difflib.get_close_matches(remove_diacritics(query), stripped_lemmas.keys(), n=5, cutoff=0.6)
        if suggestions:
            suggestion_results = [stripped_lemmas[suggestion] for suggestion in suggestions]
            return Response({
                'message': f"No matches found for '{query}'. Did you mean one of these?",
                'suggestions': suggestion_results
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': f"No matches found for '{query}' and no suggestions available."}, status=status.HTTP_404_NOT_FOUND)



class RootSearchAPIView(APIView):
    """
    API for searching lexical entries by root, with filtering, pagination, and automated documentation.
    """

    @swagger_auto_schema(
        query_serializer=RootSearchQuerySerializer,
        responses={
            200: openapi.Response(
                description="Filtered and paginated search results by root.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of results."),
                        "next": openapi.Schema(type=openapi.TYPE_STRING, description="URL for the next page of results."),
                        "previous": openapi.Schema(type=openapi.TYPE_STRING, description="URL for the previous page of results."),
                        "results": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
            404: openapi.Response(
                description="No matches found",
                examples={
                    "application/json": {
                        "message": "No matches found for the root 'كتب'."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "Root parameter is required."
                    }
                }
            ),
        },
    )
    def get(self, request):
        # Step 1: Validate query parameters
        serializer = RootSearchQuerySerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        query_params = serializer.validated_data

        root = query_params.get('root')

        # Step 2: Perform the base search
        lexical_entries = LexicalEntry.objects.filter(
            related_forms__targets=root,
            related_forms__type='root'
        ).distinct()

        if not lexical_entries.exists():
            return Response({'message': f"No matches found for the root '{root}'."}, status=status.HTTP_404_NOT_FOUND)

        # Step 3: Apply filters
        filtered_entries = QuerysetFilter(lexical_entries).apply_filters(query_params)

        # Step 4: Paginate the results
        paginator = PageNumberPagination()
        paginator.page_size_query_param = 'page_size'
        paginator.page_size = 50  # Default page size
        paginator.max_page_size = 100
        paginated_entries = paginator.paginate_queryset(filtered_entries, request)

        # Step 5: Serialize and return the paginated results
        if paginated_entries:
            serializer = LexicalEntrySerializer(paginated_entries, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response({'message': f"No matches found for the root '{root}'."}, status=status.HTTP_404_NOT_FOUND)

    


class PhraseSearchAPIView(APIView):
    """
    API for searching idioms and phrases within definitions and contexts,
    with optional filtering, pagination, diacritic handling, and fallbacks.
    """

    @swagger_auto_schema(
        query_serializer=PhraseSearchQuerySerializer,
        responses={
            200: openapi.Response(
                description="Filtered, paginated search results with support for diacritics and suggestions.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of results."),
                        "next": openapi.Schema(type=openapi.TYPE_STRING, description="URL for the next page of results."),
                        "previous": openapi.Schema(type=openapi.TYPE_STRING, description="URL for the previous page of results."),
                        "results": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
            404: openapi.Response(
                description="No matches found",
                examples={
                    "application/json": {
                        "message": "No results found for 'query'.",
                        "suggestions": ["suggestion1", "suggestion2"]
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "Query parameter is required."
                    }
                }
            ),
        },
    )
    def get(self, request):
        # Step 1: Validate query parameters using the serializer
        serializer = PhraseSearchQuerySerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        query_params = serializer.validated_data

        # Step 2: Validate and capture the required query parameter
        query = query_params.get('query', '').strip()
        if not query:
            return Response({'error': 'Query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        contains_diacritics = has_diacritics(query)
        stripped_query = remove_diacritics(query)

        # Determine if the query is a single word or a phrase
        words = query.split()
        is_phrase = len(words) > 1

        # Step 3: Perform the base search
        if is_phrase:
            # For phrases, perform exact substring matching
            definitions = Definition.objects.filter(Q(text__icontains=query if contains_diacritics else stripped_query))
            contexts = Context.objects.filter(Q(text__icontains=query if contains_diacritics else stripped_query))
        else:
            # For single words, retain the original logic
            definitions = Definition.objects.filter(Q(text__icontains=query if contains_diacritics else stripped_query))
            contexts = Context.objects.filter(Q(text__icontains=query if contains_diacritics else stripped_query))

        # Step 4: Fallback to spelling variations
        if not definitions.exists() and not contexts.exists():
            normalized_query = normalize_for_variations(stripped_query)
            definitions = Definition.objects.filter(Q(text__icontains=normalized_query))
            contexts = Context.objects.filter(Q(text__icontains=normalized_query))

        # Step 5: Aggregate results and apply filters if matches found
        if definitions.exists() or contexts.exists():
            lexical_entries = self._get_lexical_entries_from_matches(definitions, contexts)
            filtered_entries = QuerysetFilter(lexical_entries).apply_filters(query_params)

            # Step 6: Paginate the filtered results
            paginator = PageNumberPagination()
            paginator.page_size_query_param = 'page_size'
            paginator.page_size = 50  # Default page size
            paginator.max_page_size = 100
            paginated_entries = paginator.paginate_queryset(filtered_entries, request)

            if paginated_entries:
                serializer = LexicalEntrySerializer(paginated_entries, many=True)
                return paginator.get_paginated_response(serializer.data)

        # Step 7: Provide suggestions if no matches
        return self._provide_suggestions(query, stripped_query)

    def _get_lexical_entries_from_matches(self, definitions, contexts):
        """
        Helper method to aggregate matching lexical entries from definitions and contexts,
        returning a QuerySet for further filtering and pagination.
        """
        lexical_entry_ids = set()
        for definition in definitions:
            lexical_entry_ids.add(definition.sense.lexical_entry.id)
        for context in contexts:
            lexical_entry_ids.add(context.sense.lexical_entry.id)

        # Return a QuerySet of LexicalEntry objects
        return LexicalEntry.objects.filter(id__in=lexical_entry_ids)


    def _provide_suggestions(self, query, stripped_query):
        """
        Provide suggestions for the query if no matches are found.
        """
        all_lemmas = Lemma.objects.values_list('written_form', flat=True)
        stripped_lemmas = {remove_diacritics(lemma): lemma for lemma in all_lemmas}
        suggestions = difflib.get_close_matches(stripped_query, stripped_lemmas.keys(), n=5, cutoff=0.6)

        if suggestions:
            suggestion_results = [stripped_lemmas[suggestion] for suggestion in suggestions]
            return Response({
                'message': f"No matches found for '{query}'. Did you mean one of these?",
                'suggestions': suggestion_results
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': f"No matches found for '{query}' and no suggestions available.'"}, status=status.HTTP_404_NOT_FOUND)