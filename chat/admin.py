from django.contrib import admin
from django.core.paginator import Paginator
from django.core.cache import cache
from chat.models import Thread, ChatMessage


@admin.register(Thread)
class ChatThreadAdmin(admin.ModelAdmin):
	list_display = ['unique_id','first', 'second', 'updated', 'timestamp']
	search_fields = ['unique_id', 'first__name', 'second__name','first__email', 'second__email']
	readonly_fields = ['unique_id']

	
class CachingPaginator(Paginator):
	def _get_count(self):
		if not hasattr(self, "_count"):
			self._count = None
		if self._count is None:
			try:
				key = "adm:{0}:count".format(hash(self.object_list.query.__str__()))
				self._count = cache.get(key, -1)
				if self._count == -1:
					self._count = super().count
					cache.set(key, self._count, 3600)
			except:
				self._count = len(self.object_list)
			return self._count

	count = property(_get_count)

@admin.register(ChatMessage)
class RoomChatMessageAdmin(admin.ModelAdmin):
	list_filter = ['thread', 'user', 'read', 'timestamp']
	list_display = ['thread', 'user', 'message', 'read', 'timestamp']
	search_fields = ['user__name','message']
	readonly_fields = ['id', "user", "thread", 'timestamp']

	show_full_result_count = False
	paginator = CachingPaginator



