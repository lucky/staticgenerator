"""Static file generator for Django."""
import os
import stat
import tempfile
from django.http import HttpRequest
from django.core.handlers.base import BaseHandler
from django.db.models.base import ModelBase
from django.db.models.manager import Manager
from django.db.models import Model
from django.db.models.query import QuerySet
from django.utils.functional import Promise
from django.conf import settings

class DummyHandler(BaseHandler):
    """Required to process request and response middleware"""
    
    def __call__(self, request):
        self.load_middleware()
        response = self.get_response(request)
        for middleware_method in self._response_middleware:
            response = middleware_method(request, response)
            
        return response    

class StaticGeneratorException(Exception):
    pass

class StaticGenerator(object):
    """
    The StaticGenerator class is created for Django applications, like a blog,
    that are not updated per request.
    
    Usage is simple::
    
        from staticgenerator import quick_publish
        quick_publish('/', Post.objects.live(), FlatPage)
        
    The class accepts a list of 'resources' which can be any of the 
    following: URL path (string), Model (class or instance), Manager, or 
    QuerySet.
    
    As of v1.1, StaticGenerator includes file and path deletion::
        
        from staticgenerator import quick_delete
        quick_delete('/page-to-delete/')
        
    The most effective usage is to associate a StaticGenerator with a model's
    post_save and post_delete signal.
    
    """
    
    def __init__(self, *resources):
        self.resources = self.extract_resources(resources)
        self.server_name = self.get_server_name()
        try:
            self.web_root = getattr(settings, 'WEB_ROOT')
        except AttributeError:
            raise StaticGeneratorException('You must specify WEB_ROOT in settings.py')
        
    def extract_resources(self, resources):
        """Takes a list of resources, and gets paths by type"""
        extracted = []
        for resource in resources:
            
            # A URL string
            if isinstance(resource, (str, unicode, Promise)):
                extracted.append(str(resource))
                continue
            
            # A model instance; requires get_absolute_url method
            if isinstance(resource, Model):
                extracted.append(resource.get_absolute_url())
                continue
            
            # If it's a Model, we get the base Manager
            if isinstance(resource, ModelBase):
                resource = resource._default_manager
            
            # If it's a Manager, we get the QuerySet
            if isinstance(resource, Manager):
                resource = resource.all()
            
            # Append all paths from obj.get_absolute_url() to list
            if isinstance(resource, QuerySet):
                extracted += [obj.get_absolute_url() for obj in resource]
        
        return extracted
        
    def get_server_name(self):
        try:
            return getattr(settings, 'SERVER_NAME')
        except:
            pass
            
        try:
            from django.contrib.sites.models import Site
            return Site.objects.get_current().domain
        except:
            print '*** Warning ***: Using "localhost" for domain name. Use django.contrib.sites or set settings.SERVER_NAME to disable this warning.'
            return 'localhost'
    
    def get_content_from_path(self, path):
        """
        Imitates a basic http request using DummyHandler to retrieve
        resulting output (HTML, XML, whatever)
        
        """
        request = HttpRequest()
        request.path_info = path
        request.META.setdefault('SERVER_PORT', 80)
        request.META.setdefault('SERVER_NAME', self.server_name)
        
        handler = DummyHandler()
        response = handler(request)
        
        return response.content
        
    def get_filename_from_path(self, path):
        """
        Returns (filename, directory)
        Creates index.html for path if necessary
        """
        if path.endswith('/'):
            path = '%sindex.html' % path
            
        fn = os.path.join(self.web_root, path.lstrip('/')).encode('utf-8')
        return fn, os.path.dirname(fn)
        
    def publish_from_path(self, path, content=None):
        """
        Gets filename and content for a path, attempts to create directory if 
        necessary, writes to file.
        
        """
        fn, directory = self.get_filename_from_path(path)
        if not content:
            content = self.get_content_from_path(path)
        
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except:
                raise StaticGeneratorException('Could not create the directory: %s' % directory)
        
        try:
            f, tmpname = tempfile.mkstemp(dir=directory)
            os.write(f, content)
            os.close(f)
            os.chmod(tmpname, stat.S_IREAD | stat.S_IWRITE | stat.S_IWUSR | stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            os.rename(tmpname, fn)
            
        except:
            raise StaticGeneratorException('Could not create the file: %s' % fn)
            
    def delete_from_path(self, path):
        """Deletes file, attempts to delete directory"""
        fn, directory = self.get_filename_from_path(path)
        try:
            if os.path.exists(fn):
                os.remove(fn)
        except:
            raise StaticGeneratorException('Could not delete file: %s' % fn)
            
        try:
            os.rmdir(directory)
        except OSError:
            # Will fail if a directory is not empty, in which case we don't 
            # want to delete it anyway
            pass            
            
    def do_all(self, func):
        return [func(path) for path in self.resources]
    
    def delete(self):
        return self.do_all(self.delete_from_path)
        
    def publish(self):
        return self.do_all(self.publish_from_path)

def quick_publish(*resources):
    return StaticGenerator(*resources).publish()
    
def quick_delete(*resources):
    return StaticGenerator(*resources).delete()
