EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.5)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 3, 5)
	}

	StartVelocity()
	{
		keyf(0, 300)
	}

	StartVelocityRand()
	{
		keyv(0, 300, 60, 300)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")
}
