from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CarReviewLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending_review', 'Pending review')], default='pending_review', max_length=30)),
                ('message', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_logs', to='cars.car')),
                ('submitted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='car_review_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Car Review Log',
                'verbose_name_plural': 'Car Review Logs',
                'ordering': ['-created_at'],
            },
        ),
    ]
