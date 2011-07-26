def get_variables(request):

    def get_publisher():
        if hasattr(request, 'publisher'):
            return request.publisher

    context_variables = {}
    if get_publisher:
        context_variables.update({'publisher': get_publisher})
    return context_variables
