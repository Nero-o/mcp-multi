# app/utils/pagination_helper.py
class PaginacaoHelper:

    @staticmethod
    def paginate_items(items, serialize_func=None):
        if serialize_func:
            serialized_items = [serialize_func(item) for item in items]
        else:
            serialized_items = [item.serialize() for item in items]

        return serialized_items
        

    @staticmethod
    def paginate_query(query, page, per_page, serialize_func=None):

        paginated_objects = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = paginated_objects.items
        total_items = paginated_objects.total
        total_pages = paginated_objects.pages
        current_page = paginated_objects.page

        # Aplicar a função de serialização
        serialized_items = PaginacaoHelper.paginate_items(items, serialize_func)

        return {
            'totalPages': total_pages,
            'totalItems': total_items,
            'items': serialized_items,
            'currentPage': current_page,
        }
