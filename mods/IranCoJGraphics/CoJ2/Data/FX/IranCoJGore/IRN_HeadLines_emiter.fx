EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.5)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 5, 7)
	}

	StartVelocity()
	{
		keyf(0, 330)
	}

	StartVelocityRand()
	{
		keyv(0, 320, 80, 320)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")
}
