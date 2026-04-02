from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='favorite_brands',
            field=models.ManyToManyField(blank=True, related_name='favored_by_profiles', to='catalog.brand'),
        ),
    ]
