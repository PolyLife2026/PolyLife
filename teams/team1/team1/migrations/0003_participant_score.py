from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team1', '000X_last_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParticipantScore',
            fields=[
                ('score_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.BigIntegerField(db_index=True)),
                ('score', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('challenge', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='participant_scores',
                    to='team1.challenge'
                )),
            ],
            options={
                'db_table': 'participant_score',
            },
        ),
        migrations.AlterUniqueTogether(
            name='participantscore',
            unique_together={('challenge', 'user_id')},
        ),
    ]