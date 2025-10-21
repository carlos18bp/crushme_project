"""
Django management command to fix malformed HTML translations.
Re-translates content that has HTML issues.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from crushme_app.models import TranslatedContent
from crushme_app.utils.html_helpers import clean_malformed_html_translation
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fix malformed HTML in existing translations and optionally re-translate'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-only',
            action='store_true',
            help='Only fix malformed HTML tags, do not re-translate',
        )
        parser.add_argument(
            '--retranslate',
            action='store_true',
            help='Re-translate all content with HTML (strips HTML first)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )

    def handle(self, *args, **options):
        fix_only = options['fix_only']
        retranslate = options['retranslate']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('🔧 Fixing HTML translations...'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('   DRY RUN MODE - No changes will be made'))
        
        # Find translations with HTML issues
        all_translations = TranslatedContent.objects.all()
        total = all_translations.count()
        
        stats = {
            'total': total,
            'with_html': 0,
            'malformed': 0,
            'fixed': 0,
            'retranslated': 0,
            'errors': 0
        }
        
        self.stdout.write(f'   Checking {total} translations...')
        
        for trans in all_translations:
            # Check if it has HTML
            has_html_tags = '<' in trans.translated_text and '>' in trans.translated_text
            
            if not has_html_tags:
                continue
            
            stats['with_html'] += 1
            
            # Check if HTML is malformed (has spaces in tags)
            is_malformed = '< ' in trans.translated_text or ' >' in trans.translated_text
            
            if is_malformed:
                stats['malformed'] += 1
            
            try:
                if retranslate:
                    # Re-translate from clean source
                    if not dry_run:
                        self._retranslate(trans)
                    stats['retranslated'] += 1
                    
                elif fix_only or is_malformed:
                    # Just fix the malformed HTML
                    fixed_text = clean_malformed_html_translation(trans.translated_text)
                    
                    if fixed_text != trans.translated_text:
                        if not dry_run:
                            trans.translated_text = fixed_text
                            trans.save(update_fields=['translated_text'])
                        stats['fixed'] += 1
                        
                        if options['verbosity'] >= 2:
                            self.stdout.write(f'   Fixed: {trans.content_type} #{trans.object_id}')
                
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Error processing translation {trans.id}: {str(e)}")
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n✅ Summary:'))
        self.stdout.write(f'   Total translations: {stats["total"]}')
        self.stdout.write(f'   With HTML: {stats["with_html"]}')
        self.stdout.write(f'   Malformed HTML: {stats["malformed"]}')
        
        if retranslate:
            self.stdout.write(f'   Re-translated: {stats["retranslated"]}')
        else:
            self.stdout.write(f'   Fixed: {stats["fixed"]}')
        
        if stats['errors'] > 0:
            self.stdout.write(self.style.ERROR(f'   Errors: {stats["errors"]}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n   DRY RUN - No changes were made'))
            self.stdout.write('   Run without --dry-run to apply changes')
    
    @transaction.atomic
    def _retranslate(self, trans):
        """Re-translate a translation object"""
        from crushme_app.services.translation_service import TranslationService
        from crushme_app.utils.html_helpers import strip_html_tags
        
        # Get clean source text (without HTML)
        clean_source = strip_html_tags(trans.source_text)
        
        if not clean_source or not clean_source.strip():
            return
        
        # Re-translate
        translator = TranslationService(target_language=trans.target_language)
        new_translation = translator.translate(clean_source, source_language=trans.source_language)
        
        # Update
        trans.source_text = clean_source
        trans.translated_text = new_translation
        trans.save(update_fields=['source_text', 'translated_text'])
