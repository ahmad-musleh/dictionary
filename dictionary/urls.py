from django.urls import path
from .views import DictionaryRetrieveAPIView, RootSearchAPIView, PhraseSearchAPIView

urlpatterns = [
    path('search-by-keyword/', DictionaryRetrieveAPIView.as_view(), name='search-by-keyword'),
    path('search-by-root/', RootSearchAPIView.as_view(), name='search-by-root'),
    path('phrase-search/', PhraseSearchAPIView.as_view(), name='phrase-search'),
]
