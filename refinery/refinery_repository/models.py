from django.db import models

# Create your models here.
""" tables created from investigation file """
class Ontology(models.Model):
    def __unicode__(self):
        return self.term_source_name
    
    term_source_name = models.TextField()
    term_source_version = models.TextField(blank=True, null=True)
    term_source_file = models.TextField(primary_key=True)
    term_source_description = models.TextField(blank=True, null=True)
    
    class Meta:
        #even though pk is an auto-incremented number, ensures every row has a
        #unique combination of these two fields
        unique_together = ('term_source_name', 'term_source_file')

class StudyDesignDescriptor(models.Model):
    def __unicode__(self):
        return self.study_design_type
    
    study_design_type = models.TextField(primary_key=True)
    study_design_type_term_accession_number = models.TextField(blank=True, null=True)
    study_design_type_term_source_ref = models.TextField(blank=True, null=True)

class StudyFactor(models.Model):
    def __unicode__(self):
        return self.study_factor_name
    
    study_factor_name = models.TextField()
    study_factor_type = models.TextField()
    study_factor_type_term_accession_number = models.TextField(blank=True, null=True)
    study_factor_type_term_source_ref = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('study_factor_name', 'study_factor_type')

class Protocol(models.Model):
    def __unicode__(self):
        return self.study_protocol_name
    
    study_protocol_name = models.TextField(primary_key=True)
    study_protocol_type = models.TextField(blank=True, null=True)
    study_protocol_type_term_accession_number = models.TextField(blank=True, null=True)
    study_protocol_type_term_source_ref = models.TextField(blank=True, null=True)
    study_protocol_description = models.TextField(2048, blank=True, null=True)
    study_protocol_uri = models.TextField(blank=True, null=True)
    study_protocol_version = models.TextField(blank=True, null=True)
    study_protocol_parameters_name = models.TextField(blank=True, null=True)
    study_protocol_parameters_name_term_accession_number = models.TextField(blank=True, null=True)
    study_protocol_parameters_name_term_source_ref = models.TextField(blank=True, null=True)
    study_protocol_components_name = models.TextField(blank=True, null=True)
    study_protocol_components_type = models.TextField(blank=True, null=True)
    study_protocol_components_type_term_accession_number = models.TextField(blank=True, null=True)
    study_protocol_components_type_term_source_ref = models.TextField(blank=True, null=True)

class Investigation(models.Model):
    def __unicode__(self):
        return self.study_identifier

    study_identifier = models.TextField(primary_key=True)
    study_title = models.TextField()
    study_description = models.TextField()
    study_public_release_date = models.DateField(blank=True, null=True)
    #study_submission_date = models.DateField(blank=True, null=True)
    study_file_name = models.TextField()
    #assay attributes
    study_assay_measurement_type = models.TextField(blank=True, null=True)
    study_assay_measurement_type_term_accession_number = models.TextField(blank=True, null=True)
    study_assay_measurement_type_term_source_ref = models.TextField(blank=True, null=True)
    study_assay_technology_type = models.TextField(blank=True, null=True)
    study_assay_technology_type_term_accession_number = models.TextField(blank=True, null=True)
    study_assay_technology_type_term_source_ref = models.TextField(blank=True, null=True)
    study_assay_technology_platform = models.TextField(blank=True, null=True)
    study_assay_file_name = models.TextField()
    
    #0, 1, or more ontologies can be used for many different investigations
    ontologies = models.ManyToManyField(Ontology, blank=True, null=True)
    #an investigation can have 0, 1, or more study_factors
    study_factors = models.ManyToManyField(StudyFactor, blank=True, null=True)
    #one or more study_design_descriptors can be used for different investigations
    study_design_descriptors = models.ManyToManyField(StudyDesignDescriptor)
    protocols = models.ManyToManyField(Protocol)
    
class Publication(models.Model):
    def __unicode__(self):
        return str(self.study_pubmed_id)
    
    study_pubmed_id = models.IntegerField(primary_key=True)
    study_publication_doi = models.TextField(blank=True, null=True)
    study_publication_author_list = models.TextField(blank=True, null=True)
    study_publication_title = models.TextField(blank=True, null=True)
    study_publication_status = models.TextField(blank=True, null=True)
    study_publication_status_term_accession_number = models.TextField(blank=True, null=True)
    study_publication_status_term_source_ref = models.TextField(blank=True, null=True)

    investigation = models.ForeignKey(Investigation)

class Investigator(models.Model):
    def __unicode__(self):
        name = "%s, %s %s" % (self.study_person_last_name, 
                              self.study_person_first_name, 
                              self.study_person_mid_initials)
        return name

    study_person_email = models.EmailField(max_length=1024, primary_key=True)
    study_person_last_name = models.TextField()
    study_person_first_name = models.TextField()
    study_person_mid_initials = models.TextField(blank=True, null=True)
    study_person_phone = models.TextField(blank=True, null=True)
    study_person_fax = models.TextField(blank=True, null=True)
    study_person_address = models.TextField()
    study_person_affiliation = models.TextField()
    study_person_roles = models.TextField()
    study_person_roles_term_accession_number = models.TextField(blank=True, null=True)
    study_person_roles_term_source_ref = models.TextField(blank=True, null=True)
    
    investigations = models.ManyToManyField(Investigation)
    

""" tables created from study or assay file """
class SubType(models.Model):
    def __unicode__(self):
        return self.type

    type = models.TextField(primary_key=True)

class Comment(models.Model):
    def __unicode__(self):
        return "%s: %s" % (self.type.type, self.value)
    value = models.TextField()
    type = models.ForeignKey(SubType)
    
    #comments can belong to both studies and assays, but only one at a time
    #so make both "optional" so that only one needs specifying at a time
    study = models.ForeignKey('Study', blank=True, null=True)
    assay = models.ForeignKey('Assay', blank=True, null=True)

    
""" tables created from study file """
class Study(models.Model):
    def __unicode__(self):
        return self.source_name
    source_name = models.TextField(primary_key=True)
    sample_name = models.TextField()
    material_type = models.TextField(blank=True, null=True)
    provider = models.TextField(blank=True, null=True) 
    
    #usually more than one protocol per study
    protocols = models.ManyToManyField(Protocol)
    investigation = models.ForeignKey(Investigation)

class Characteristic(models.Model):
    def __unicode__(self):
        return "%s: %s" % (self.type.type, self.value)

    value = models.TextField()
    term_source_ref = models.TextField(blank=True, null=True)
    term_accession_number = models.TextField(blank=True, null=True)
    
    type = models.ForeignKey(SubType)
    study = models.ForeignKey(Study)

    
""" tables created from assay file """   
class RawData(models.Model):
    def __unicode__(self):
        return self.raw_data_file

    raw_data_file = models.TextField()
    data_transformation_name = models.TextField()

class ProcessedData(models.Model):
    def __unicode__(self):
        return self.derived_arrayexpress_ftp_file

    derived_arrayexpress_ftp_file = models.TextField()
    derived_data_file = models.TextField()
    
class Assay(models.Model):
    def __unicode__(self):
        return self.sample_name

    sample_name = models.TextField()
    material_type = models.TextField(blank=True, null=True)
    assay_name = models.TextField(blank=True, null=True)
    extract_name = models.TextField(blank=True, null=True)
    performer = models.TextField(blank=True, null=True)
    technology_type = models.TextField(blank=True, null=True)
    scan_name = models.TextField(blank=True, null=True)
    labeled_extract_name = models.TextField(blank=True, null=True)
    label = models.TextField(blank=True, null=True)
    hybridization_assay_name = models.TextField(blank=True, null=True)
    array_design_ref = models.TextField(blank=True, null=True)
    protocol_ref = models.TextField(blank=True, null=True)
    normalization_name = models.TextField(blank=True, null=True)
    
    #one raw/processed data file may be associated with multiple assays
    raw_data = models.ManyToManyField(RawData, null=True, blank=True)
    processed_data = models.ManyToManyField(ProcessedData, blank=True, null=True)
    #protocols can be recycled
    protocols = models.ManyToManyField(Protocol)
    
    investigation = models.ForeignKey(Investigation)
    study = models.ForeignKey(Study)

class FactorValue(models.Model):
    def __unicode__(self):
        return "%s: %s" % (self.type.type, self.value)

    value = models.TextField()
    term_source_ref = models.TextField(blank=True, null=True)
    term_accession_number = models.TextField(blank=True, null=True)
    
    type = models.ForeignKey(SubType)
    assay = models.ForeignKey(Assay)


"""can be used for anything that's not a factor value that has
the format super-type[sub-type] in the header (e.g. Parameter_Value, Unit)
"""    
class HaveSubtype(models.Model):
    def __unicode__(self):
        return "%s: %s" % (self.type, self.value)
    
    value = models.TextField()
    type = models.ForeignKey(SubType)
    super_type = models.TextField()
    assay = models.ForeignKey(Assay)