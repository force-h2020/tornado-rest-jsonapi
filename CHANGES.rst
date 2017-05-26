Tornado WebAPI CHANGELOG
========================

What's new in Tornado WebAPI 0.6.0
----------------------------------

This releases introduces backward incompatible changes.

Summary
~~~~~~~

- Removed global registry (#47)
- Introduced Transport, Parser, Renderer, Serializer and Deserializers to
  add flexibility to REST protocol (#48)
- Resource is now called ResourceHandler. Web handlers have been renamed
  to more appropriate names. (#49)
- The following changes have been introduced as a result of Pull Request #50
  - Introduced traitlets-based declarative definition of resources.
  - ``registry.registered_types`` is now ``registered_handlers``
  - register() now accepts only one parameter: the handler.
  - pluralization are now declared at the Resource level, rather than at
    registration time.

What's new in Tornado WebAPI 0.5.0
----------------------------------

Summary
~~~~~~~

- Javascript interface now returns high level results instead of Ajax responses. (#42)
- WebAPI Exceptions in validation routines are propagated as is, instead of being converted (#41)
- Added Resource.validate_identifier to validate the identifier. It must return the
  identifier (#40)
- Resource.validate() is now Resource.validate_representation(). It must return the
  representation, either unchanged or after modifications. (#39)
- Fix: missing files are now correctly released (#37, #38)

What's new in Tornado WebAPI 0.4.0
----------------------------------

Summary
~~~~~~~

- Automatic creation of JavaScript API to access the resources. (#33)

What's new in Tornado WebAPI 0.3.0
----------------------------------

Summary
~~~~~~~

- Added Exists exception (#27)
- Force the resource identifier to be a string, 
  allowing transparent return of a numerical id (#28)
- Added validation method to check the incoming representation (#29)

What's new in Tornado WebAPI 0.2.0
----------------------------------

Summary
~~~~~~~

- Support for multiple registries (#16)
- Deprecated exception BadRequest in favor of BadRepresentation (#21)

What's new in Tornado WebAPI 0.1.0
----------------------------------

Summary
~~~~~~~

- Initial porting from simphony-remote 

