from dataclasses import dataclass, field, asdict

@dataclass
class Job:
    """Representa una oferta de trabajo."""
    title: str = 'N/A'
    company: str = 'N/A'
    url: str = 'N/A'
    description: str = 'N/A'
    location: str = 'N/A'
    salary: str = 'N/A'
    created: str = 'N/A'
    source: str = 'N/A'
    job_type: str = 'N/A'
    jooble_id: str = 'N/A'
    technologies: list = field(default_factory=list)
    
    def to_dict(self):
        """Convierte el Job a diccionario para compatibilidad con PostgreSQL."""
        return asdict(self)
