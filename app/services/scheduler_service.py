from app.models.publication import PublicationModel

class SchedulerService:
    @staticmethod
    def get_scheduled_publications():
        return PublicationModel.get_all()

    @staticmethod
    def schedule_publication(titulo, mensaje, dias, hora, producto_id=None, imagen_url=None):
        if isinstance(dias, list):
            dias_str = ','.join(dias)
        else:
            dias_str = str(dias)
            
        return PublicationModel.create(
            titulo=titulo,
            mensaje=mensaje,
            dias_semana=dias_str,
            hora=hora,
            producto_id=producto_id,
            imagen_url=imagen_url
        )