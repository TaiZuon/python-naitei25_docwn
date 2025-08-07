from django.core.management.base import BaseCommand
from django.db.models import Count
from novels.models import Chapter
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Fix duplicate chapter slugs by regenerating them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find chapters with duplicate slugs
        duplicate_slugs = (
            Chapter.objects
            .values('slug')
            .annotate(count=Count('slug'))
            .filter(count__gt=1)
            .order_by('slug')
        )
        
        if not duplicate_slugs:
            self.stdout.write(
                self.style.SUCCESS('No duplicate chapter slugs found.')
            )
            return

        self.stdout.write(
            self.style.WARNING(f'Found {len(duplicate_slugs)} duplicate slugs')
        )

        for dup in duplicate_slugs:
            slug = dup['slug']
            count = dup['count']
            
            self.stdout.write(f'\nProcessing slug: {slug} ({count} duplicates)')
            
            # Get all chapters with this slug, ordered by creation date
            chapters = Chapter.objects.filter(slug=slug).order_by('created_at')
            
            # Keep the first chapter's slug unchanged, update the rest
            for i, chapter in enumerate(chapters):
                if i == 0:
                    self.stdout.write(f'  Keeping original: {chapter.id} - {chapter.title}')
                    continue
                
                # Generate new unique slug for this chapter
                volume_slug = slugify(chapter.volume.name) if chapter.volume.name else f'tap-{chapter.volume.position}'
                
                if chapter.title and chapter.title.strip():
                    chapter_slug = slugify(chapter.title.strip())
                else:
                    chapter_slug = f'chuong-{chapter.position}'
                
                base_slug = f'{volume_slug}-{chapter_slug}'
                
                # Ensure uniqueness
                new_slug = base_slug
                counter = 1
                while Chapter.objects.filter(slug=new_slug).exclude(pk=chapter.pk).exists():
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1
                
                self.stdout.write(f'  Updating: {chapter.id} - {chapter.title}')
                self.stdout.write(f'    Old slug: {chapter.slug}')
                self.stdout.write(f'    New slug: {new_slug}')
                
                if not dry_run:
                    chapter.slug = new_slug
                    chapter.save()

        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nDry run completed. Use --dry-run=False to apply changes.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nSuccessfully fixed duplicate chapter slugs.')
            )
