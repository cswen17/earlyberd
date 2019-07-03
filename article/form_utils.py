from binascii import a2b_base64
from mimetypes import guess_type
from tempfile import NamedTemporaryFile

from django import forms
from django.core.files.uploadedfile import UploadedFile


IMAGE_HEADER = 'data:image/png;base64,'
JPEG_IMAGE_HEADER = 'data:image/jpeg;base64'

class UserWidget(forms.widgets.Widget):
    template_name = 'user_subform.html'

    # initial values
    user_first_name_textinput_name = 'user_first_name'
    user_first_name_textinput_id = 'user-first-name'
    user_first_name_textinput_label = 'First Name'

    user_last_name_textinput_name = 'user_last_name'
    user_last_name_textinput_id = 'user-last-name'
    user_last_name_textinput_label = 'Last Name'

    user_email_address_textinput_name = 'user_email_address'
    user_email_address_textinput_id = 'user-email-address'
    user_email_address_textinput_label = 'Email Address'

    def __init__(self, attrs=None, **kwargs):
        self.user_first_name_textinput_name = kwargs.get(
            'fn_name', self.user_first_name_textinput_name)
        self.user_first_name_textinput_id = kwargs.get(
            'fn_id', self.user_first_name_textinput_id)
        self.user_first_name_textinput_label = kwargs.get(
            'fn_label', self.user_first_name_textinput_label)

        self.user_last_name_textinput_name = kwargs.get(
            'ln_name', self.user_last_name_textinput_name)
        self.user_last_name_textinput_id = kwargs.get(
            'ln_id', self.user_last_name_textinput_id)
        self.user_last_name_textinput_label = kwargs.get(
            'ln_label', self.user_last_name_textinput_label)

        self.user_email_address_textinput_name = kwargs.get(
            'ea_name', self.user_email_address_textinput_name)
        self.user_email_address_textinput_id = kwargs.get(
            'ea_id', self.user_email_address_textinput_id)
        self.user_email_address_textinput_label = kwargs.get(
            'ea_label', self.user_email_address_textinput_label)

        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        ref = dict(
            fnn=self.user_first_name_textinput_name,
            fni=self.user_first_name_textinput_id,
            fnl=self.user_first_name_textinput_label,
            lnn=self.user_last_name_textinput_name,
            lni=self.user_last_name_textinput_id,
            lnl=self.user_last_name_textinput_label,
            ean=self.user_email_address_textinput_name,
            eai=self.user_email_address_textinput_id,
            eal=self.user_email_address_textinput_label,
        )
        widget = context['widget']
        widget['user_first_name_textinput_name'] = ref['fnn']
        widget['user_first_name_textinput_id'] = ref['fni']
        widget['user_first_name_textinput_label'] = ref['fnl']
        widget['user_last_name_textinput_name'] = ref['lnn']
        widget['user_last_name_textinput_id'] = ref['lni']
        widget['user_last_name_textinput_label'] = ref['lnl']
        widget['user_email_address_textinput_name'] = ref['ean']
        widget['user_email_address_textinput_id'] = ref['eai']
        widget['user_email_address_textinput_label'] = ref['eal']
        first_name, last_name = widget['value'].split(' ')
        widget['first_name'] = first_name
        widget['last_name'] = last_name
        return context

    def value_from_datadict(self, data, files, name):
        result = {}
        result['first_name'] = data.get('user_first_name', '')
        result['last_name'] = data.get('user_last_name', '')
        return result


class UserField(forms.Field):

    widget = UserWidget


class CoverImageWidget(forms.widgets.Widget):

    """
    Image File Upload widget that also hosts a
    (https://foliotek.github.io/Croppie/)[croppie] instance
    for cropping a thumbnail out of an image
    """

    template_name = 'croppable_image.html'
    croppie_height = 200
    croppie_width = 720
    image_height = 400
    image_width = 1440

    # initial values
    is_large_croppie = False
    is_image_linked = False

    cover_image_id = 'id_cover_image'
    cover_image_name = 'cover_image'
    cover_image_label = 'Cover Image'
    cover_image_metadata_name = 'cover_image_name' # html
    metadata_name = 'cover_image_metadata'
    
    croppie_container_name = 'croppie_container'
    upload_message = 'Upload a cover image'
    linked_message = 'Reuse previous image'
    
    button_override_classes = ''
    done_cropping_label = 'Done'

    # derive from CoverImageWidget instance
    linked_id = cover_image_id

    def __init__(self, attrs=None, **kwargs):
        prefix = kwargs.get('prefix')
        if prefix is None:
            raise AttributeError(
                'You must specify a CoverImageWidget prefix')
        self.prefix = prefix

        self.croppie_height = kwargs.get(
            'croppie_height',
            self.croppie_height,
        )
        self.croppie_width = kwargs.get(
            'croppie_width',
            self.croppie_width,
        )
        self.image_height = kwargs.get(
            'image_height',
            self.image_height,
        )
        self.image_width = kwargs.get(
            'image_width',
            self.image_width,
        )

        self.is_large_croppie = kwargs.get(
            'is_large_croppie',
            self.is_large_croppie,
        )
        self.is_image_linked = kwargs.get(
            'is_image_linked',
            self.is_image_linked,
        )

        self.cover_image_id = kwargs.get(
            'cover_image_id',
            self.cover_image_id,
        )
        self.cover_image_name = kwargs.get(
            'cover_image_name',
            self.cover_image_name,
        )
        self.cover_image_label = kwargs.get(
            'cover_image_label',
            self.cover_image_label,
        )
        self.cover_image_metadata_name = kwargs.get(
            'cover_image_metadata_name',
            self.cover_image_metadata_name,
        )
        self.metadata_name = kwargs.get(
            'metadata_name',
            self.metadata_name,
        )

        self.croppie_container_name = kwargs.get(
            'croppie_container_name',
            self.croppie_container_name,
        )
        self.upload_message = kwargs.get(
            'upload_message',
            self.upload_message,
        )

        self.button_override_classes = kwargs.get(
            'button_override_classes',
            self.button_override_classes,
        )
        self.done_cropping_label = kwargs.get(
            'done_cropping_label',
            self.done_cropping_label,
        )

        self.linked_id = kwargs.get(
            'linked_id',
            self.linked_id,
        )

        super(CoverImageWidget, self).__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        widget = context['widget']
        widget['croppie_height'] = self.croppie_height
        widget['croppie_width'] = self.croppie_width
        widget['image_height'] = self.image_height
        widget['image_width'] = self.image_width
        widget['is_large_croppie'] = self.is_large_croppie
        widget['is_image_linked'] = self.is_image_linked
        widget['cover_image_id'] = self.cover_image_id 
        widget['cover_image_name'] = self.cover_image_name
        widget['cover_image_label'] = self.cover_image_label
        widget['cover_image_metadata_name'] = self.cover_image_metadata_name or None
        widget['metadata_name'] = self.metadata_name
        widget['croppie_container_name'] = self.croppie_container_name
        widget['upload_message'] = self.upload_message
        widget['button_override_classes'] = self.button_override_classes
        widget['done_cropping_label'] = self.done_cropping_label
        widget['linked_id'] = self.linked_id
        widget['linked_message'] = self.linked_message
        value = widget.get('value', '')

        # helper/derived context values
        widget['cover_image_url'] = self.cover_image_url(value)
        widget['cover_image_filename'] = self.cover_image_filename(value)
        widget['prefix'] = self.prefix

        return context

    def value_from_datadict(self, data, files, name):
        """
        Returns the cropped image, its height, and its width
        """
        image_name = data.get(
            self.cover_image_metadata_name, 'default.jpg')
        content_type, encoding = guess_type(image_name)

        image_header = IMAGE_HEADER

        cover_image_binascii = data[self.cover_image_name]
        cover_image_binascii = cover_image_binascii[len(image_header):]
        cover_image_binary = a2b_base64(cover_image_binascii) 
        print('-------')
        print(self.cover_image_name)
        print(data[self.cover_image_name])
        print(cover_image_binary)
        print('-------')
        

        # create a  file
        """
        named_temp_file = NamedTemporaryFile() 
        size = named_temp_file.write(cover_image_binary)
        """
        named_file = open('tmp-{}'.format(image_name), 'w+b')
        size = named_file.write(cover_image_binary)
        named_file.close()
        tf = open('tmp-{}'.format(image_name), 'r+b')
        image = UploadedFile(
            tf,
            # named_temp_file,
            name,
            'tmp-{}'.format(image_name),
            content_type,
            size,
            encoding,
        )
        return image

    def cover_image_url(self, value):
        if not value:
            return ''
        parts = value.split('media/')
        return 'media/{}'.format(parts[-1])

    def cover_image_filename(self, value):
        if not value:
            return ''
        parts = value.split('media/')
        return parts[-1]


class CoverImageField(forms.Field):

    def __init__(self, *args, **kwargs):
        self.widget = CoverImageWidget(
            is_large_croppie=True,
            prefix='cover',
        )
        super(CoverImageField, self).__init__(*args, **kwargs)


class CoverImageThumbnailField(forms.Field):

    def __init__(self, *args, **kwargs):
        self.widget = CoverImageWidget(
            croppie_height=124,
            croppie_width=256,
            image_height=124,
            image_width=256,
            is_large_croppie=False,
            cover_image_name='cover_image_thumbnail',
            cover_image_metadata_name='cover_image_thumbnail_name',
            cover_image_id='id_cover_image_thumbnail',
            prefix='thumbnail',
            is_image_linked=True,
        )
        super(CoverImageThumbnailField, self).__init__(*args, **kwargs)
