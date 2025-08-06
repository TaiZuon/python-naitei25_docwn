from django.core.management.base import BaseCommand
from django.utils.text import slugify
from novels.models import Chapter


class Command(BaseCommand):
    help = 'Generate slugs for chapters that have empty slugs'

    def handle(self, *args, **options):
        self.stdout.write('Fixing chapters with empty slugs...')
        
        # Find chapters with empty or null slugs
        chapters_without_slugs = Chapter.objects.filter(slug__in=['', None])
        count = chapters_without_slugs.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No chapters found with empty slugs'))
            return
        
        self.stdout.write(f'Found {count} chapters with empty slugs')
        
        fixed_count = 0
        for chapter in chapters_without_slugs:
            try:
                # Generate slug from title
                if chapter.title and chapter.title.strip():
                    base_slug = slugify(chapter.title.strip())
                else:
                    base_slug = f'chuong-{chapter.position}'
                    
                if not base_slug:  # If slugify returns empty string
                    base_slug = f'chuong-{chapter.position}'
                
                # Ensure uniqueness within the same novel
                slug = base_slug
                counter = 1
                while Chapter.objects.filter(
                    volume__novel=chapter.volume.novel, 
                    slug=slug
                ).exclude(pk=chapter.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                chapter.slug = slug
                chapter.save()
                fixed_count += 1
                
                self.stdout.write(f'Fixed chapter: {chapter.title} -> {slug}')
                
            except Exception as e:
                self.stdout.write(f'Error fixing chapter {chapter.id}: {e}')
                continue
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully fixed {fixed_count} out of {count} chapters')
        )
