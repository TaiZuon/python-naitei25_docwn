from django.core.management.base import BaseCommand
from novels.models import Chunk


class Command(BaseCommand):
    help = 'Fix chunk content by replacing literal \\n with actual newlines'

    def handle(self, *args, **options):
        self.stdout.write("Fixing chunk content newlines...")
        
        chunks_to_fix = Chunk.objects.filter(content__contains='\\n')
        total_count = chunks_to_fix.count()
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS("No chunks need fixing."))
            return
        
        self.stdout.write(f"Found {total_count} chunks with literal \\n characters")
        
        fixed_count = 0
        for chunk in chunks_to_fix:
            old_content = chunk.content
            # Replace literal \n with actual newlines
            new_content = old_content.replace('\\n', '\n')
            
            if old_content != new_content:
                chunk.content = new_content
                chunk.save()
                fixed_count += 1
                
                # Show first 5 examples
                if fixed_count <= 5:
                    self.stdout.write(f"Fixed chunk {chunk.id}: {chunk.chapter.title}")
                    self.stdout.write(f"  Before: {repr(old_content[:100])}...")
                    self.stdout.write(f"  After:  {repr(new_content[:100])}...")
                    self.stdout.write("")
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully fixed {fixed_count} chunks out of {total_count} found")
        )
